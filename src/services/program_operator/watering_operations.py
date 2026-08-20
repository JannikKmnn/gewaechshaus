import asyncio
import httpx
import numpy as np

from typing import Literal

from datetime import datetime, timedelta, timezone
from logging import Logger


async def fetch_temperature_data(
    start: datetime,
    end: datetime,
    sensor: Literal["inside", "up", "outside"],
    url: str,
    logger: Logger,
    client: httpx.AsyncClient,
):
    try:
        temperature_data = await client.post(
            url=f"{url}/data/temperature_{sensor}",
            json={
                "start_time": start.isoformat(),
                "measurement": "Temperature",
                "end_time": end.isoformat(),
            },
        )
        temperature_data.raise_for_status()
        logger.info(
            f"Received temperature data with response {temperature_data.status_code}"
        )
    except httpx.HTTPError as err:
        logger.error(f"Requesting temperature data failed due to {err}")
        return []

    if len(temperature_data.json()) == 0:
        return []

    return [temp["value"] for temp in temperature_data.json()]


async def calculate_watering_score(
    url: str,
    logger: Logger,
):

    current_day = datetime.now(tz=timezone.utc)

    start_time = datetime(
        current_day.year,
        current_day.month,
        current_day.day,
        hour=10,
        tzinfo=timezone.utc,
    )

    end_time = datetime(
        current_day.year,
        current_day.month,
        current_day.day,
        hour=15,
        tzinfo=timezone.utc,
    )

    async with httpx.AsyncClient() as client:
        inside, outside = await asyncio.gather(
            fetch_temperature_data(
                start=start_time,
                end=end_time,
                sensor="inside",
                url=url,
                logger=logger,
                client=client,
            ),
            fetch_temperature_data(
                start=start_time,
                end=end_time,
                sensor="outside",
                url=url,
                logger=logger,
                client=client,
            ),
        )

    if len(inside) == 0 or len(outside) == 0:
        logger.warning("Received no inside data for the day. Returning water score 0.0")
        return 0.0

    mean_inside = np.mean(inside)

    delta = np.abs(np.array(inside) - np.array(outside))
    mean_delta = np.mean(delta)

    temperature_score = np.clip(
        (mean_inside - 15) / (35 - 15),
        0,
        1,
    )

    solar_score = np.clip(
        (mean_delta - 0) / (10 - 0),
        0,
        1,
    )

    water_score = temperature_score * 0.5 + solar_score * 0.5

    logger.warning(
        f"""
    Calculated scores between {start_time} and {end_time}:
        - temperature score: {temperature_score}
        - solar score: {solar_score}
        - water score: {water_score}
    """
    )

    return water_score


async def run_scheduled_watering(
    url: str,
    logger: Logger,
    duration: timedelta | None = None,
):
    """
    Calls watering API endpoint to start watering for a given duration.
    If no duration is provided, it will use the default duration set in the API.
    """

    base_url = f"{url}/watering/run_watering"

    read_write_timeout = (
        max(duration.total_seconds() + 80, 30) if duration is not None else 1000
    )

    timeout = httpx.Timeout(
        30.0,
        read=read_write_timeout,
        write=read_write_timeout,
    )

    # Adding time to duration based on weather measurement indicators
    # during the day (only evening)
    now = datetime.now(tz=timezone.utc)
    if duration is not None and now > datetime(
        now.year, now.month, now.day, 15, tzinfo=timezone.utc
    ):
        water_score = await calculate_watering_score(
            url=base_url,
            logger=logger,
        )
        duration += timedelta(minutes=15 * water_score)

    async with httpx.AsyncClient(timeout=timeout) as client:
        logger.warning(f"Starting Watering API call with duration {duration}...")
        try:
            watering_time_seconds = None
            if duration is not None:
                watering_time_seconds = min(
                    int(duration.total_seconds()),
                    20 * 60,
                )

            response = await client.post(
                url=base_url,
                json={"watering_time_seconds": (watering_time_seconds)},
            )
            response.raise_for_status()
            return response
        except httpx.HTTPError as err:
            logger.error(f"Watering call failed due to {err}")
            return None
