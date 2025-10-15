import adafruit_dht
import asyncio
import board
import logging

from datetime import datetime
from pydantic import Field
from pydantic_settings import BaseSettings

from w1thermsensor import W1ThermSensor

GPIO_PIN_HUMIDITY_TEMPERATURE_SENSOR = board.D4


class Settings(BaseSettings):

    measure_interval_seconds: int = Field(default=20)
    display_switch_interval: int = Field(default=10)

    temperature_outside_sensor_id: str = Field(default="000000b47976")
    temperature_inside_sensor_id: str = Field(default="000000b998e3")

    log_lvl: str = Field(default="INFO")


settings = Settings()

logging.basicConfig(level=settings.log_lvl)
logger = logging.getLogger(__name__)


async def measure_humidity_temperature(device_object: adafruit_dht.DHT11):

    try:

        temperature_c = device_object.temperature
        humidity = device_object.humidity

    except RuntimeError as error:

        logger.warning(
            f"Measuring humidity and temperature ran into runtime error: {error}"
        )
        temperature_c = None
        humidity = None

    except Exception as error:

        logger.warning(
            f"Measuring humidity and temperature ran into unknown error: {error}"
        )
        temperature_c = None
        humidity = None

    return humidity, temperature_c


async def measure_temperature(sensor_object: W1ThermSensor | None):

    if not sensor_object:
        return None

    try:

        temperature_c = sensor_object.get_temperature()

    except Exception as error:

        logger.warning(f"Measuring temperature ran into unknown error: {error}")
        temperature_c = None

    return temperature_c


async def main():

    humidityTemperatureDevice = adafruit_dht.DHT11(
        GPIO_PIN_HUMIDITY_TEMPERATURE_SENSOR, use_pulseio=False
    )

    temperature_sensors = W1ThermSensor.get_available_sensors()

    temperatureOutsideSensor = next(
        (sens for sens in temperature_sensors
        if sens.id == settings.temperature_outside_sensor_id), 
        None
    )
    temperatureInsideSensor = next(
        (sens for sens in temperature_sensors
        if sens.id == settings.temperature_inside_sensor_id), 
        None
    )

    logger.info(
        f"""
        Using Sensors:
         - Humidity: {humidityTemperatureDevice}
         - Temperature Outside: {temperatureOutsideSensor}
         - Temperature Inside: {temperatureInsideSensor}
        """
    )

    while True:

        results = await asyncio.gather(
            measure_humidity_temperature(device_object=humidityTemperatureDevice),
            measure_temperature(sensor_object=temperatureOutsideSensor),
            measure_temperature(sensor_object=temperatureInsideSensor),
        )

        logger.info(
            f"""
            Measurements {datetime.now()}:
            - Humidity: {results[0][0]}%, 
            - Temperature (Middle): {results[0][1]}°C
            - Temperature (Outside): {results[1]}°C
            - Temperature (Inside): {results[2]}°C
            """
        )

        await asyncio.sleep(settings.measure_interval_seconds)


if __name__ == "__main__":
    asyncio.run(main())
