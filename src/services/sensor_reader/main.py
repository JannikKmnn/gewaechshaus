import adafruit_dht
import asyncio
import board
import logging

from datetime import datetime
from pydantic import Field
from pydantic_settings import BaseSettings

from src.services.sensor_reader.display import display_task
from src.services.sensor_reader.influxdb import write_to_influxdb
from src.services.sensor_reader.mqtt import publish_message
from src.services.sensor_reader.setup import (
    setup_display,
    setup_mqtt,
    setup_influxdb,
    setup_soil_moisture_sensors,
    setup_temperature_sensors,
)

from src.models.enums import MeasureUnit, MQTTResponse, Position, SensorType
from src.models.sensor import (
    Sensor,
    HumiditySensor,
    TemperatureSensor,
    SoilMoistureSensor,
)

GPIO_PIN_HUMIDITY_TEMPERATURE_SENSOR = board.D4


class Settings(BaseSettings):

    measure_interval_seconds: int = Field(default=60)

    temperature_outside_sensor_id: str = Field(default="000000b47976")
    temperature_inside_sensor_id: str = Field(default="000000b998e3")

    soil_moisture_sensor_channel_back: int = Field(default=23)
    soil_moisture_sensor_channel_front: int = Field(default=24)

    lcd_i2c_address: int = Field(default=0x27)  # try 0x3F if not works
    lcd_columns: int = Field(default=16)
    lcd_rows: int = Field(default=2)

    # MQTT settings

    mqtt_broker: str = Field(default="test")
    mqtt_port: int = Field(default=1111)
    mqtt_user: str = Field(default="greenhouse")
    mqtt_password: str = Field("")

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

    ### 1. 1 Setup humidity sensor ###

    humidityTemperatureDevice = adafruit_dht.DHT11(
        GPIO_PIN_HUMIDITY_TEMPERATURE_SENSOR, use_pulseio=False
    )

    humidity_sensor = HumiditySensor(
        identifier="humidity",
        display_name="humidity",
        type=SensorType.HUMIDITY,
        unit=MeasureUnit.PERCENT,
        position=Position.UP,
        logger=logger,
        sensor_obj=humidityTemperatureDevice,
    )

    sensors.append(humidity_sensor)

    ### 1.2 Setup temperature sensors ###

    temperature_sensors: list[TemperatureSensor] = setup_temperature_sensors(
        outside_sensor_id=settings.temperature_outside_sensor_id,
        inside_sensor_id=settings.temperature_inside_sensor_id,
        sensor_up=humidityTemperatureDevice,
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

    mqtt_client = None

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

            ### 3. Initial mqtt client connect ###
            # and reconnection every time client fails
            # TODO add cron scheduler instead
            if mqtt_client is None:
                mqtt_client = setup_mqtt(
                    broker=settings.mqtt_broker,
                    port=settings.mqtt_port,
                    user=settings.mqtt_user,
                    password=settings.mqtt_password,
                    logger=logger,
                )

            results = await asyncio.gather(*[sensor.measure() for sensor in sensors])

            result_dict = {
                sens.identifier: value for value, sens in zip(results, sensors)
            }

            display_dict = {
                sens.display_name: f"{value} {sens.unit.value if sens.unit else ''}"
                for value, sens in zip(results, sensors)
            }

            logger.info(
                f"""
                Measurements {datetime.now()}:
                {display_dict}
                """
            )

            ### 4. Send MQTT message, save influxdb record and display measurements ###
            mqtt_response, influxdb_response, _ = await asyncio.gather(
                publish_message(
                    client=mqtt_client, result_dict=result_dict, logger=logger
                ),
                write_to_influxdb(
                    client=influxdb_asnyc_client,
                    bucket=settings.influxdb_bucket,
                    result_dict=result_dict,
                    sensors=sensors,
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
                MQTT response: {mqtt_response.value}
                InfluxDB response: {influxdb_response.value}
                """
            )

            if mqtt_response == MQTTResponse.CLIENT_CRASHED:
                mqtt_client = None


if __name__ == "__main__":
    asyncio.run(main())
