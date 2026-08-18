import asyncio
import httpx
import logging

import numpy as np

from datetime import datetime, timezone, timedelta
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):

    # for API calls
    vite_api_base_url: str = Field(...)

    log_lvl: str = Field(default="WARNING")


# Setup
settings = Settings()

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=settings.log_lvl,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

LOOKBACK_DAYS = 70


async def fetch_temperature_data(
    start: datetime,
    end: datetime,
    sensor: Literal["inside", "up", "outside"],
):
    async with httpx.AsyncClient() as client:
        try:
            temperature_data = await client.post(
                url=f"{settings.vite_api_base_url}/data/temperature_{sensor}",
                json={
                    "start_time": start.isoformat(),
                    "measurement": "Temperature",
                    "end_time": end.isoformat(),
                },
            )
            logger.info(
                f"Received temperature data with response {temperature_data.status_code}"
            )
        except httpx.HTTPError as err:
            logger.error(f"Requesting temperature data failed due to {err}")
            temperature_data = None

    return [temp["value"] for temp in temperature_data.json()]


async def main():

    current_day = datetime.now(tz=timezone.utc)

    for _ in range(LOOKBACK_DAYS):
        current_day = current_day - timedelta(days=1)

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

        inside, outside = await asyncio.gather(
            fetch_temperature_data(start=start_time, end=end_time, sensor="inside"),
            fetch_temperature_data(start=start_time, end=end_time, sensor="outside"),
        )

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

        print(
            f"{start_time.isoformat()} - {end_time.isoformat()}: temp={round(temperature_score, 2)}, sol={round(solar_score, 2)}, score={round(water_score, 2)}"
        )


if __name__ == "__main__":

    asyncio.run(main())
    print("Test done.")
