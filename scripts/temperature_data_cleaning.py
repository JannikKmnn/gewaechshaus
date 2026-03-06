import asyncio
import httpx
import logging

import numpy as np

from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

load_dotenv()

from pydantic import Field
from pydantic_settings import BaseSettings

from influxdb_client import Point
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from src.services.sensor_reader.setup import setup_influxdb


class Settings(BaseSettings):

    # for API calls
    vite_api_base_url: str = Field(...)

    log_lvl: str = Field(default="INFO")

    # InfluxDB settings

    influxdb_host: str = Field(default="https://localhost:8000")
    influxdb_org: str = Field(default="main")
    influxdb_bucket: str = Field(default="greenhouse")
    influxdb_token: str = Field(default="")
    influxdb_timeout: int = Field(default=10000)  # 10s


# Setup
settings = Settings()

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=settings.log_lvl,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


DATA_OFFSET_START_TIME = datetime(2025, 12, 18, 17, 34, 18, tzinfo=timezone.utc)
DATA_OFFSET_END_TIME = datetime(2026, 1, 4, 12, 10, 17, tzinfo=timezone.utc)


async def fetch_temperature_data(
    start: datetime,
    end: datetime,
):
    async with httpx.AsyncClient() as client:
        try:
            temperature_data = await client.post(
                url=f"{settings.vite_api_base_url}/data/",
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

    return temperature_data


async def write_to_influxdb(
    points: list[Point],
    client: InfluxDBClientAsync,
):
    try:
        _ = await client.write_api().write(
            bucket=settings.influxdb_bucket,
            record=points,
        )
        logger.info(f"Writing Data: {points} in client {client}")
    except Exception as err:
        logger.error(f"Inserting DB data failed due to: {err}")


def get_new_inside_measurements(
    vals,
):

    inside_temperatures = [
        meas for meas in vals if meas["field"] == "temperature_inside"
    ]
    outside_temperatures = [
        meas for meas in vals if meas["field"] == "temperature_outside"
    ]
    up_temperatures = [meas for meas in vals if meas["field"] == "temperature_up"]

    new_insides = []

    for idx, temps in enumerate(
        zip(up_temperatures, outside_temperatures, inside_temperatures)
    ):
        (up, outside, inside) = temps

        new_inside_value = round(np.mean([up["value"], outside["value"]]), 4)
        logger.debug(up)
        logger.debug(outside)
        logger.debug(new_inside_value)

        inside["value"] = float(new_inside_value)

        logger.debug(inside)

        new_insides.append(inside)

    return new_insides


async def main():

    influx_client = setup_influxdb(
        host=settings.influxdb_host,
        org=settings.influxdb_org,
        token=settings.influxdb_token,
        timeout=settings.influxdb_timeout,
        logger=logger,
    )

    data = await fetch_temperature_data(
        start=DATA_OFFSET_START_TIME,
        end=DATA_OFFSET_START_TIME + timedelta(minutes=15),
    )

    vals = data.json()

    new_inside_values = get_new_inside_measurements(vals=vals)
    logger.info(f"New values: {new_inside_values}")
    upload_values = [
        Point(value["measurement"])
        .field(value["field"], value["value"])
        .time(datetime.fromisoformat(value["timestamp"]))
        for value in new_inside_values
    ]

    logger.info(upload_values)

    async with influx_client:
        await write_to_influxdb(points=upload_values, client=influx_client)


if __name__ == "__main__":
    asyncio.run(main())
