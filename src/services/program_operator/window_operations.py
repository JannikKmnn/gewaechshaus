import asyncio
import httpx
from datetime import datetime, timedelta, timezone
from logging import Logger

from typing import Literal, Optional

from src.models.enums import ProgramInstruction
from src.services.program_operator.condition_handling import get_instructions


async def fetch_temp_measurements(
    client: httpx.AsyncClient,
    ds_request_minutes: int,
    temperature_sensor_identifier: str,
    url: str,
    logger: Logger,
) -> httpx.Response | None:
    """
    Fetches temperature measurements from the DB via API calls.
    Returned data serves as foundation for actions on greenhouse actuators.

    Args:
        client (httpx.AsyncClient): http client to interact with API.
        ds_request_minutes (int): time window in minutes, usually the cron schedule interval
        temperature_sensor_identifier (str): identifier of the temperature sensor
        url (str): base url of the API
        logger (Logger): logger instance for logging messages

    Returns:
        temperature_data (httpx.Response | None): Temperature measurements from the
            last cron_schedule_minutes as httpx.Response object. If None, error
            has been raised.
    """
    req_end = datetime.now(tz=timezone.utc)
    req_start = req_end - timedelta(minutes=ds_request_minutes)

    try:
        temperature_data = await client.post(
            url=f"{url}/data/{temperature_sensor_identifier}",
            json={
                "start_time": req_start.isoformat(),
                "measurement": "Temperature",
                "end_time": req_end.isoformat(),
            },
        )
        temperature_data.raise_for_status()
        logger.info(
            f"Received temperature data with response {temperature_data.status_code}"
        )
    except httpx.HTTPError as err:
        logger.error(f"Requesting temperature data failed due to {err}")
        temperature_data = None

    return temperature_data


async def fetch_window_status(
    client: httpx.AsyncClient,
    window_position: Literal["left", "right"],
    url: str,
    logger: Logger,
) -> httpx.Response | None:
    """
    Fetches window status from the DB via API calls.
    Returned data indicate if certain actions (opening, closing) are required.

    Args:
        client (httpx.AsyncClient): http client to interact with API.
        window_position (left | right): which window is requested
        url (str): base url of the API
        logger (Logger): logger instance for logging messages

    Returns:
        temperature_data (httpx.Response | None): Window status from API
            as httpx.Response object. If None, error has been raised.
    """
    try:
        status = await client.get(
            url=f"{url}/window/status/{window_position}",
        )
        status.raise_for_status()
        logger.info(f"Received window status with response {status.status_code}")
    except httpx.HTTPError as err:
        logger.error(f"Requesting {window_position} window status failed due to {err}")
        status = None

    return status


async def fetch_window_configurations(
    client: httpx.AsyncClient,
    window_position: Literal["left", "right"],
    url: str,
    logger: Logger,
) -> httpx.Response | None:
    """
    Fetches window configs from the DB via API calls.
    Allows dynamically setting thresholds for window events.

    Args:
        client (httpx.AsyncClient): http client to interact with API.
        window_position (left | right): which window is requested
        url (str): base url of the API
        logger (Logger): logger instance for logging messages

    Returns:
        configurations (httpx.Response | None): Window configs from API
            as httpx.Response object. If None, error has been raised.
    """
    try:
        configurations = await client.get(
            url=f"{url}/window/config/{window_position}",
        )
        configurations.raise_for_status()
        logger.info(
            f"Received window configs with response {configurations.status_code}"
        )
    except httpx.HTTPError as err:
        logger.error(f"Requesting {window_position} window config failed due to {err}")
        configurations = None

    return configurations


async def act_on_windows(
    movement: Literal["open", "close"],
    url: str,
    logger: Logger,
    window_position: Optional[Literal["left", "right"]] = None,
) -> httpx.Response | None:
    """
    Calls API endpoint to perform operations on windows.

    Args:
        movement (open | close): wether window(s) should be opened or closed
        window_position (left | right | None): which window is supposed to be
            operated on. If None, both windows are called.

    Returns:
        response (httpx.Response | None): API response or None if http call failed.
    """

    client_timeout = httpx.Timeout(30.0)

    base_url = f"{url}/window/{movement}"
    if window_position:
        base_url += f"/{window_position}"

    async with httpx.AsyncClient(timeout=client_timeout) as client:

        try:
            response = await client.post(
                url=base_url,
            )
            response.raise_for_status()
        except httpx.HTTPError as err:
            logger.error(f"Window movement call failed due to {err}")
            response = None

    return response


async def check_and_perform_operations(
    response: list[httpx.Response],
    url: str,
    logger: Logger,
):
    """
    Performs opening/closing on windows if certain conditions are met.

    Args:
        response (list[httpx.Response]): list of responses to initial API calls,
            containing measurements and left/right window status.
    """
    left_window_threshold, right_window_threshold = (
        response[3].json()["inside_temperature_opening_threshold"],
        response[4].json()["inside_temperature_opening_threshold"],
    )

    measurements = [rec["value"] for rec in response[0].json()]

    if not measurements:
        logger.warning("No measurements received.")
        return

    # define opening/closing conditions
    close_windows_condition = any(meas < left_window_threshold for meas in measurements)
    both_windows_condition = all(meas > right_window_threshold for meas in measurements)

    left_window_status, right_window_status = (
        response[1].json()["status"],
        response[2].json()["status"],
    )

    logger.info(
        f"""
        Received measurements: {measurements}
        Left window status: {left_window_status}
        Right window status: {right_window_status}
        Left window threshold: {left_window_threshold}
        Right window threshold: {right_window_threshold}
    """
    )

    instructions: list[ProgramInstruction] = get_instructions(
        close_windows_condition=close_windows_condition,
        both_windows_condition=both_windows_condition,
        left_window_status=left_window_status,
        right_window_status=right_window_status,
        logger=logger,
    )

    operations = []
    for ins in instructions:
        if ins == ProgramInstruction.NO_OPERATION:
            continue

        movement = ins.movement()
        position = ins.position()

        logger.info(
            f"""
            Calling window API with movement {movement}
            and position {position}
        """
        )

        operations.append(
            act_on_windows(
                movement=movement,
                window_position=position,
                url=url,
                logger=logger,
            )
        )

    if len(operations) > 0:
        responses = await asyncio.gather(*operations)
        return responses

    return


async def run_window_program(
    interval_minutes: int,
    temperature_sensor_identifier: str,
    api_url: str,
    logger: Logger,
):

    timeout = httpx.Timeout(30.0)

    async with httpx.AsyncClient(timeout=timeout) as client:

        response = await asyncio.gather(
            *[
                fetch_temp_measurements(
                    client=client,
                    ds_request_minutes=interval_minutes,
                    temperature_sensor_identifier=temperature_sensor_identifier,
                    url=api_url,
                    logger=logger,
                ),
                fetch_window_status(
                    client=client,
                    window_position="left",
                    url=api_url,
                    logger=logger,
                ),
                fetch_window_status(
                    client=client,
                    window_position="right",
                    url=api_url,
                    logger=logger,
                ),
                fetch_window_configurations(
                    client=client,
                    window_position="left",
                    url=api_url,
                    logger=logger,
                ),
                fetch_window_configurations(
                    client=client,
                    window_position="right",
                    url=api_url,
                    logger=logger,
                ),
            ],
            return_exceptions=True,
        )

    if any(isinstance(res, Exception) or res is None for res in response):
        logger.error("One or more API calls failed.")
        return

    await check_and_perform_operations(response=response, url=api_url, logger=logger)
