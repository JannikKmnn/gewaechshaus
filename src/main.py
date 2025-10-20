import adafruit_dht
import asyncio
import board
import logging

from datetime import datetime
from pydantic import Field
from pydantic_settings import BaseSettings

from decorators import retry

from RPLCD.i2c import CharLCD
from w1thermsensor import W1ThermSensor

import RPi.GPIO as GPIO

GPIO_PIN_HUMIDITY_TEMPERATURE_SENSOR = board.D4


class Settings(BaseSettings):

    measure_interval_seconds: int = Field(default=40)

    temperature_outside_sensor_id: str = Field(default="000000b47976")
    temperature_inside_sensor_id: str = Field(default="000000b998e3")

    soil_moisture_sensor_channel_back: int = Field(default=23)
    soil_moisture_sensor_channel_front: int = Field(default=24)

    lcd_i2c_address: str = Field(default="0x27")  # try 0x3F if not works
    lcd_columns: int = Field(default=16)
    lcd_rows: int = Field(default=2)

    log_lvl: str = Field(default="INFO")


settings = Settings()

logging.basicConfig(level=settings.log_lvl)
logger = logging.getLogger(__name__)


@retry(times=3)
async def measure_humidity_temperature(device_object: adafruit_dht.DHT11):

    try:

        temperature_c = device_object.temperature
        humidity = device_object.humidity

    except Exception as error:

        logger.warning(f"Measuring humidity and temperature ran into error: {error}")
        temperature_c = None
        humidity = None

    return humidity, temperature_c


@retry(times=2)
async def measure_temperature(sensor_object: W1ThermSensor | None):

    if not sensor_object:
        return None

    try:

        temperature_c = sensor_object.get_temperature()

    except Exception as error:

        logger.warning(f"Measuring temperature ran into error: {error}")
        temperature_c = None

    return temperature_c


@retry(times=2)
async def measure_soil_moisture(pin):

    try:

        value = GPIO.input(pin)
        is_wet = value == GPIO.LOW

    except Exception as error:

        logger.warning(f"Measuring soil moisture ran into error: {error}")
        is_wet = None

    return is_wet


def display_measurements(lcd_object: CharLCD | None, line_1: str, line_2: str):

    if not lcd_object:
        return None

    lcd_object.clear()

    # make sure only the first {lcd_columns} characters are displayed
    lcd_object.write_string(line_1[: settings.lcd_columns])
    if line_2:
        lcd_object.cursor_pos = (1, 0)
        lcd_object.write_string(line_2[: settings.lcd_columns])


async def main():

    ### Setup humidity sensor ###
    humidityTemperatureDevice = adafruit_dht.DHT11(
        GPIO_PIN_HUMIDITY_TEMPERATURE_SENSOR, use_pulseio=False
    )

    ### Setup temperature sensors ###
    temperature_sensors = W1ThermSensor.get_available_sensors()

    temperatureOutsideSensor = next(
        (
            sens
            for sens in temperature_sensors
            if sens.id == settings.temperature_outside_sensor_id
        ),
        None,
    )
    temperatureInsideSensor = next(
        (
            sens
            for sens in temperature_sensors
            if sens.id == settings.temperature_inside_sensor_id
        ),
        None,
    )

    ### Setup soil moisture sensors ###
    GPIO.setmode(GPIO.BCM)

    pin_back = settings.soil_moisture_sensor_channel_back
    pin_front = settings.soil_moisture_sensor_channel_front
    GPIO.setup(pin_back, GPIO.IN)
    GPIO.setup(pin_front, GPIO.IN)

    ### Setup lcd display ###
    lcdDisplay = CharLCD(
        i2c_expander="PCF8574",
        address=settings.lcd_i2c_address,
        cols=settings.lcd_columns,
        rows=settings.lcd_rows,
    )

    logger.info(
        f"""
        Using Sensors:
         - Humidity: {humidityTemperatureDevice}
         - Temperature Outside: {temperatureOutsideSensor}
         - Temperature Inside: {temperatureInsideSensor}
         - Soil Moisture Back: {pin_back}
         - Soil Moisture Front: {pin_front}
        Using Display:
         - LCD Display: {lcdDisplay}
        """
    )

    while True:

        results = await asyncio.gather(
            measure_humidity_temperature(device_object=humidityTemperatureDevice),
            measure_temperature(sensor_object=temperatureOutsideSensor),
            measure_temperature(sensor_object=temperatureInsideSensor),
            measure_soil_moisture(pin=pin_back),
            measure_soil_moisture(pin=pin_front),
        )

        result_dict = {
            "humidity": results[0][0],
            "temperature mid": results[0][1],
            "temperature out": results[1],
            "temperature in": results[2],
            "soil moisture b": results[3],
            "soil moisture f": results[4],
        }

        logger.info(
            f"""
            Measurements {datetime.now()}:
            - Humidity: {result_dict['humidity']}%, 
            - Temperature (Middle): {result_dict['temperature mid']}°C
            - Temperature (Outside): {result_dict['temperature out']}°C
            - Temperature (Inside): {result_dict['temperature in']}°C
            - Soil is wet (back): {result_dict['soil moisture back']}
            - Soil is wet (front): {result_dict['soil moisture front']}
            """
        )

        for sensor, value in result_dict.items():
            display_measurements(lcd_object=lcdDisplay, line_1=sensor, line_2=value)
            await asyncio.sleep(
                settings.measure_interval_seconds / len(result_dict.values())
            )


if __name__ == "__main__":
    asyncio.run(main())
