import adafruit_dht
import asyncio
import board
import logging

from datetime import datetime
from pydantic import Field
from pydantic_settings import BaseSettings

from decorators import retry
from display import display_task
from mqtt import setup_client, publish_message

from services.sensor_reader.src.models.mqtt import MQTTProperties

from RPLCD.i2c import CharLCD
from w1thermsensor import W1ThermSensor

import RPi.GPIO as GPIO  # type: ignore

GPIO_PIN_HUMIDITY_TEMPERATURE_SENSOR = board.D4


class Settings(BaseSettings):

    measure_interval_seconds: int = Field(default=40)

    temperature_outside_sensor_id: str = Field(default="000000b47976")
    temperature_inside_sensor_id: str = Field(default="000000b998e3")

    soil_moisture_sensor_channel_back: int = Field(default=23)
    soil_moisture_sensor_channel_front: int = Field(default=24)

    lcd_i2c_address: int = Field(default=0x27)  # try 0x3F if not works
    lcd_columns: int = Field(default=16)
    lcd_rows: int = Field(default=2)

    # MQTT settings

    mqtt_broker: str = Field(default="test")
    mqtt_port: int = Field(default="1111")
    mqtt_user: str = Field(default="greenhouse")
    mqtt_password: str = Field("123456")

    log_lvl: str = Field(default="INFO")


settings = Settings()

logging.basicConfig(level=settings.log_lvl)
logger = logging.getLogger(__name__)


@retry(times=4, logger=logger)
async def measure_humidity_temperature(device_object: adafruit_dht.DHT11):

    temperature_c = device_object.temperature
    humidity = device_object.humidity

    return humidity, temperature_c


@retry(times=2)
async def measure_temperature(sensor_object: W1ThermSensor | None):

    if not sensor_object:
        return None

    temperature_c = sensor_object.get_temperature()

    return temperature_c


@retry(times=2)
async def measure_soil_moisture(pin):

    value = GPIO.input(pin)
    is_wet = value == GPIO.LOW

    return is_wet


def display_measurements(lcd_object: CharLCD | None, line_1: str, line_2: str):

    if not lcd_object:
        return None

    lcd_object.clear()

    # make sure only the first {lcd_columns} characters are displayed
    lcd_object.write_string(line_1[: settings.lcd_columns])
    if line_2:
        lcd_object.cursor_pos = (1, 0)
        lcd_object.write_string(str(line_2))


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
    try:
        if isinstance(settings.lcd_i2c_address, int):
            lcd_address = settings.lcd_i2c_address
        else:
            lcd_address = int(settings.lcd_i2c_address)
        lcdDisplay = CharLCD(
            i2c_expander="PCF8574",
            address=lcd_address,
            port=1,
            cols=settings.lcd_columns,
            rows=settings.lcd_rows,
            charmap="A00",
        )
    except Exception as err:
        logger.warning(f"LCD display could not be detected due to: {err}")
        lcdDisplay = None

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

    ### Setup mqtt client ###

    mqtt_client_properties = MQTTProperties(
        broker=settings.mqtt_broker,
        port=settings.mqtt_port,
        user=settings.mqtt_user,
        password=settings.mqtt_password,
    )

    mqtt_client = setup_client(
        client_properties=mqtt_client_properties,
        logger=logger,
        start_loop=True,
    )

    while True:

        results = await asyncio.gather(
            measure_humidity_temperature(device_object=humidityTemperatureDevice),
            measure_temperature(sensor_object=temperatureOutsideSensor),
            measure_temperature(sensor_object=temperatureInsideSensor),
            measure_soil_moisture(pin=pin_back),
            measure_soil_moisture(pin=pin_front),
        )

        soil_moisture_b = "wet" if results[3] else "dry"
        soil_moisture_f = "wet" if results[4] else "dry"

        result_dict = {
            "humidity": f"{results[0][0]}%",
            "temperature up": f"{results[0][1]}°C",
            "temperature out": f"{results[1]}°C",
            "temperature in": f"{results[2]}°C",
            "soil moisture b": soil_moisture_b,
            "soil moisture f": soil_moisture_f,
        }

        logger.info(
            f"""
            Measurements {datetime.now()}:
            - Humidity: {result_dict['humidity']}, 
            - Temperature (Up): {result_dict['temperature up']}
            - Temperature (Outside): {result_dict['temperature out']}
            - Temperature (Inside): {result_dict['temperature in']}
            - Soil is wet (back): {result_dict['soil moisture b']}
            - Soil is wet (front): {result_dict['soil moisture f']}
            """
        )

        _ = await asyncio.gather(
            display_task(
                lcd_object=lcdDisplay,
                result_dict=result_dict,
                measure_interval=settings.measure_interval_seconds,
            ),
            publish_message(client=mqtt_client, result_dict=result_dict),
        )


if __name__ == "__main__":
    asyncio.run(main())
