"""Main Script to execute on windows/watering automation based on given program."""

from datetime import datetime, timezone, timedelta

import asyncio
import logging
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Literal, Optional

from src.models.enums import ProgramInstruction
from src.services.program_operator.condition_handling import get_instructions


class Settings(BaseSettings):

    temperature_sensor: str = Field(default="temperature_inside")
    night_mode_on: bool = Field(default=False)

    # cron scheduling time also for dataset request size
    cron_schedule_minutes: int = Field(default=15)

    # for API calls
    vite_api_base_url: str = Field(...)

    log_lvl: str = Field(default="INFO")


# Setup
settings = Settings()

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=settings.log_lvl,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def fetch_temp_measurements(client: httpx.AsyncClient) -> httpx.Response | None:
    """
    Fetches temperature measurements from the DB via API calls.
    Returned data serves as foundation for actions on greenhouse actuators.

    Args:
        client (httpx.AsyncClient): http client to interact with API.

    Returns:
        temperature_data (httpx.Response | None): Temperature measurements from the
            last cron_schedule_minutes as httpx.Response object. If None, error
            has been raised.
    """
    req_end = datetime.now(tz=timezone.utc)
    req_start = req_end - timedelta(minutes=settings.cron_schedule_minutes)

    try:
        temperature_data = await client.post(
            url=f"{settings.vite_api_base_url}/data/{settings.temperature_sensor}",
            json={
                "start_time": req_start.isoformat(),
                "measurement": "Temperature",
                "end_time": req_end.isoformat(),
            },
        )
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
) -> httpx.Response | None:
    """
    Fetches window status from the DB via API calls.
    Returned data indicate if certain actions (opening, closing) are required.

    Args:
        client (httpx.AsyncClient): http client to interact with API.
        window_position (left | right): which window is requested

    Returns:
        temperature_data (httpx.Response | None): Window status from API
            as httpx.Response object. If None, error has been raised.
    """
    try:
        status = await client.get(
            url=f"{settings.vite_api_base_url}/window/status/{window_position}",
        )
        logger.info(f"Received window status with response {status.status_code}")
    except httpx.HTTPError as err:
        logger.error(f"Requesting {window_position} window status failed due to {err}")
        status = None

    return status


async def fetch_window_configurations(
    client: httpx.AsyncClient,
    window_position: Literal["left", "right"],
) -> httpx.Response | None:
    """
    Fetches window configs from the DB via API calls.
    Allows dynamically setting thresholds for window events.

    Args:
        client (httpx.AsyncClient): http client to interact with API.
        window_position (left | right): which window is requested

    Returns:
        configurations (httpx.Response | None): Window configs from API
            as httpx.Response object. If None, error has been raised.
    """
    try:
        configurations = await client.get(
            url=f"{settings.vite_api_base_url}/window/config/{window_position}",
        )
        logger.info(
            f"Received window configs with response {configurations.status_code}"
        )
    except httpx.HTTPError as err:
        logger.error(f"Requesting {window_position} window config failed due to {err}")
        configurations = None

    return configurations


async def act_on_windows(
    movement: Literal["open", "close"],
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

    base_url = f"{settings.vite_api_base_url}/window/{movement}"
    if window_position:
        base_url += f"/{window_position}"

    async with httpx.AsyncClient(timeout=client_timeout) as client:

        try:
            response = await client.post(
                url=base_url,
            )
        except httpx.HTTPError as err:
            logger.error(f"Window movement call failed due to {err}")
            response = None

    return response


async def check_and_perform_operations(
    response: list[httpx.Response],
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

    # define opening/closing conditions
    close_windows_condition = any(meas < left_window_threshold for meas in measurements)
    both_windows_condition = all(meas > right_window_threshold for meas in measurements)

    left_window_status, right_window_status = (
        response[1].json()["status"],
        response[2].json()["status"],
    )

    logger.warning(
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
            )
        )

    if len(operations) > 0:
        responses = await asyncio.gather(*operations)
        return responses

    return


async def run_program():

    timeout = httpx.Timeout(30.0)

    async with httpx.AsyncClient(timeout=timeout) as client:

        response = await asyncio.gather(
            *[
                fetch_temp_measurements(client=client),
                fetch_window_status(
                    client=client,
                    window_position="left",
                ),
                fetch_window_status(
                    client=client,
                    window_position="right",
                ),
                fetch_window_configurations(
                    client=client,
                    window_position="left",
                ),
                fetch_window_configurations(
                    client=client,
                    window_position="right",
                ),
            ],
            return_exceptions=True,
        )

    if any(isinstance(res, Exception) or res is None for res in response):
        logger.error("One or more API calls failed.")
        return

    await check_and_perform_operations(response=response)


async def main():

    logger.warning(
        f"""
            INFO: starting program operator with configurations
                - left window temperature threshold: {settings.left_window_temp_thres} °C
                - left window temperature threshold: {settings.both_window_temp_thres} °C
                - based on sensor: {settings.temperature_sensor}
        """
    )
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        run_program,
        trigger="cron",
        minute=f"*/{settings.cron_schedule_minutes}",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )

    scheduler.start()

    while True:
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
