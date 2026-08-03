"""Main Script to execute on windows/watering automation based on given program."""

import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pydantic import Field
from pydantic_settings import BaseSettings

from src.services.program_operator.watering_operations import run_scheduled_watering
from src.services.program_operator.window_operations import run_window_program


class Settings(BaseSettings):

    temperature_sensor: str = Field(default="temperature_inside")
    night_mode_on: bool = Field(default=False)

    # cron scheduling time for windows, also for dataset request size
    window_cron_schedule_minutes: int = Field(default=15)

    # watering cron hours
    watering_cron_hour_morning: int = Field(default=9)
    watering_cron_hour_evening: int = Field(default=20)

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


async def main():

    logger.warning(
        f"""
        INFO: starting program operator based on sensors:
         - Temperature Sensor: {settings.temperature_sensor}
         - Soil Moisture Sensors: both for watering
        """
    )

    scheduler = AsyncIOScheduler()

    # 1. Window Job
    window_kwargs = {
        "interval_minutes": settings.window_cron_schedule_minutes,
        "temperature_sensor_identifier": settings.temperature_sensor,
        "api_url": settings.vite_api_base_url,
        "logger": logger,
    }
    scheduler.add_job(
        run_window_program,
        kwargs=window_kwargs,
        trigger="cron",
        minute=f"*/{settings.window_cron_schedule_minutes}",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )

    logger.info(
        f"""
    Window program added to scheduler.
        kwargs: {window_kwargs}
        minute: {settings.window_cron_schedule_minutes}
    """
    )

    # 2. Watering CRON Job
    watering_hours = (
        f"{settings.watering_cron_hour_morning},{settings.watering_cron_hour_evening}"
    )
    scheduler.add_job(
        run_scheduled_watering,
        kwargs={
            "url": settings.vite_api_base_url,
            "logger": logger,
        },
        trigger="cron",
        hour=watering_hours,
        minute=0,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )

    logger.info(
        f"""
    Watering program added to scheduler.
        watering hours: {watering_hours}
    """
    )

    scheduler.start()

    logger.info(f"Scheduler started.")

    while True:
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
