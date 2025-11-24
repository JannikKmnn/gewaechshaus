import asyncio
import logging

from datetime import datetime
from pydantic import Field
from pydantic_settings import BaseSettings

from src.services.sensor_reader.display import display_task
from src.services.sensor_reader.influxdb import write_to_influxdb
from src.services.sensor_reader.setup import (
    setup_display,
    setup_influxdb,
    setup_barometric_sensor,
    setup_soil_moisture_sensors,
    setup_temperature_sensors,
)

from src.models.data import Measurement
from src.models.sensor import (
    Sensor,
    BarometricSensor,
    TemperatureSensor,
    SoilMoistureSensor,
)


class Settings(BaseSettings):

    measure_interval_seconds: int = Field(default=60)

    temperature_outside_sensor_id: str = Field(default="000000b47976")
    temperature_inside_sensor_id: str = Field(default="000000b998e3")

    soil_moisture_sensor_channel_back: int = Field(default=23)
    soil_moisture_sensor_channel_front: int = Field(default=24)

    bme280_i2c_address: int = Field(default=0x76)  # try 0x77 if not works
    i2c_port: int = Field(default=1)

    lcd_i2c_address: int = Field(default=0x27)  # try 0x3F if not works
    lcd_columns: int = Field(default=16)
    lcd_rows: int = Field(default=2)

    # InfluxDB settings

    influxdb_host: str = Field(default="https://localhost:8000")
    influxdb_org: str = Field(default="main")
    influxdb_bucket: str = Field(default="greenhouse")
    influxdb_token: str = Field(default="")
    influxdb_timeout: int = Field(default=10000)  # 10s

    log_lvl: str = Field(default="INFO")


settings = Settings()

logging.basicConfig(level=settings.log_lvl)
logger = logging.getLogger(__name__)


def init_sensor_group() -> list[Sensor]:

    sensors: list[Sensor] = []

    ### 1. 1 Setup barometric sensor ###

    barometric_sensor: BarometricSensor = setup_barometric_sensor(
        i2c_address=settings.bme280_i2c_address,
        i2c_port=settings.i2c_port,
    )

    sensors.append(barometric_sensor)

    ### 1.2 Setup temperature sensors ###

    temperature_sensors: list[TemperatureSensor] = setup_temperature_sensors(
        outside_sensor_id=settings.temperature_outside_sensor_id,
        inside_sensor_id=settings.temperature_inside_sensor_id,
    )

    sensors.extend(temperature_sensors)

    ### 1.3 Setup soil moisture sensors ###
    soil_moisture_sensors: list[SoilMoistureSensor] = setup_soil_moisture_sensors(
        pin_back=settings.soil_moisture_sensor_channel_back,
        pin_front=settings.soil_moisture_sensor_channel_front,
    )

    sensors.extend(soil_moisture_sensors)

    return sensors


async def main():

    sensors: list[Sensor] = init_sensor_group()

    ### 1. Setup lcd display ###

    lcd_display = setup_display(
        i2c_address=settings.lcd_i2c_address,
        lcd_columns=settings.lcd_columns,
        lcd_rows=settings.lcd_rows,
        logger=logger,
    )

    logger.info(
        f"""
        Using Sensors:
         {sensors}
        Using Display:
         - LCD Display: {lcd_display}
        """
    )

    ### 2. Setup influxdb client ###

    influxdb_asnyc_client = setup_influxdb(
        host=settings.influxdb_host,
        org=settings.influxdb_org,
        token=settings.influxdb_token,
        timeout=settings.influxdb_timeout,
        logger=logger,
    )

    async with influxdb_asnyc_client:

        while True:

            # TODO add cron scheduler

            results = await asyncio.gather(*[sensor.measure() for sensor in sensors])

            measurement_results: list[Measurement] = []
            for res in results:
                measurement_results.extend(res)

            display_dict = {
                mr.display_name: f"{mr.value} {mr.unit.value if mr.unit else ''}"
                for mr in measurement_results
            }

            logger.debug(
                f"""
                Measurements {datetime.now()}:
                {display_dict}
                """
            )

            ### 3. Save influxdb record and display measurements ###
            influxdb_response, _ = await asyncio.gather(
                write_to_influxdb(
                    client=influxdb_asnyc_client,
                    bucket=settings.influxdb_bucket,
                    measurement_results=measurement_results,
                    logger=logger,
                ),
                display_task(
                    lcd_object=lcd_display,
                    display_dict=display_dict,
                    measure_interval=settings.measure_interval_seconds,
                ),
            )

            logger.debug(
                f"""
                InfluxDB response: {influxdb_response.value}
                """
            )


if __name__ == "__main__":
    asyncio.run(main())
