import asyncio
import logging

from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

load_dotenv()

from pydantic import Field
from pydantic_settings import BaseSettings

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


async def delete_from_influxdb(
    start: datetime,
    end: datetime,
    client: InfluxDBClientAsync,
):
    try:
        _ = await client.delete_api().delete(
            start=start,
            stop=end,
            bucket=settings.influxdb_bucket,
            predicate='_measurement="Temperature" AND _field="temperature_inside"',
        )
    except Exception as err:
        logger.error(f"Deleting DB data failed due to: {err}")


async def main():

    influx_client = setup_influxdb(
        host=settings.influxdb_host,
        org=settings.influxdb_org,
        token=settings.influxdb_token,
        timeout=settings.influxdb_timeout,
        logger=logger,
    )

    async with influx_client:
        await delete_from_influxdb(
            start=DATA_OFFSET_START_TIME,
            end=DATA_OFFSET_START_TIME + timedelta(minutes=5),
            client=influx_client,
        )


if __name__ == "__main__":
    asyncio.run(main())
