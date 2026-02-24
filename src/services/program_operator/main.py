"""Main Script to execute on windows/watering automation based on given program."""

from datetime import datetime, timezone, timedelta

import asyncio
import logging
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Literal, Optional


class Settings(BaseSettings):

    # program variables
    left_window_temp_thres: int = Field(default=25)
    both_window_temp_thres: int = Field(default=28)
    temperature_sensor: str = Field(default="temperature_inside")
    night_mode_on: bool = Field(default=False)

    # cron scheduling time also for dataset request size
    cron_schedule_minutes: int = Field(default=5)

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


async def act_on_windows(
    movement: Literal["open", "close"],
    window_position: Optional[Literal["left", "right"]] = None,
):

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
    """
    measurements = [rec["value"] for rec in response[0].json()]

    # define opening/closing conditions
    close_windows_condition = any(
        meas < settings.left_window_temp_thres for meas in measurements
    )
    both_window_condition = all(
        meas > settings.both_window_temp_thres for meas in measurements
    )

    left_window_status, right_window_status = (
        response[1].json()["status"],
        response[2].json()["status"],
    )

    if close_windows_condition:
        # Close both windows (too cold inside)
        if left_window_status == right_window_status == "closed":
            logger.info("All good, too cold and windows closed.")
            return

        if left_window_status == right_window_status == "open":
            logger.info("Too cold and both windows open, closing...")
            return

        if left_window_status == "open":
            # only left open
            logger.info("Too cold and left window open, closing...")
            return

        logger.info("Too cold and right window open, closing...")
    elif both_window_condition:
        # Open both windows (too hot inside)
        if left_window_status == right_window_status == "open":
            logger.info("All good, Too hot and both windows open.")
            return

        if left_window_status == right_window_status == "closed":
            logger.info("Too hot and windows closed, opening...")
            return

        if right_window_status == "closed":
            # only right closed
            logger.info("Too hot and right window closed, opening...")
            return

        logger.info("Too hot and left window closed, opening...")
    else:
        # Open only left window
        if left_window_status == right_window_status == "open":
            logger.info("Close right window...")
            return

        if left_window_status == right_window_status == "closed":
            logger.info("Open left window...")
            return

        if left_window_status == "closed" and right_window_status == "open":
            logger.info("Open left window and close right...")
            return

        logger.info("All good.")


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
            ],
            return_exceptions=True,
        )

    if any(isinstance(res, Exception) or res is None for res in response):
        logger.error("One or more API calls failed.")
        return

    await check_and_perform_operations(response=response)


async def main():
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
