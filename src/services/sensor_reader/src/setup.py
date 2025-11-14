from logging import Logger
from typing import Optional

from adafruit_dht import DHT11
from w1thermsensor import W1ThermSensor
from RPLCD.i2c import CharLCD

from mqtt import setup_client

from models.enums import Position, SensorType, MeasureUnit
from models.mqtt import MQTTProperties
from models.sensor import TemperatureSensor, SoilMoistureSensor


def setup_display(
    i2c_address: int,
    lcd_columns: int,
    lcd_rows: int,
    logger: Logger,
) -> CharLCD | None:
    try:
        lcdDisplay = CharLCD(
            i2c_expander="PCF8574",
            address=i2c_address,
            port=1,
            cols=lcd_columns,
            rows=lcd_rows,
            charmap="A00",
        )
    except Exception as err:
        logger.warning(f"LCD display could not be detected due to: {err}")
        lcdDisplay = None

    return lcdDisplay


def setup_mqtt(
    broker: str,
    port: int,
    user: str,
    password: str,
    logger: Logger,
):

    mqtt_client_properties = MQTTProperties(
        broker=broker,
        port=port,
        user=user,
        password=password,
    )

    mqtt_client = setup_client(
        client_properties=mqtt_client_properties,
        logger=logger,
        start_loop=True,
    )

    return mqtt_client


def setup_soil_moisture_sensors(
    pin_back: int,
    pin_front: int,
) -> list[SoilMoistureSensor]:

    soil_moisture_sensor_back = SoilMoistureSensor(
        identifier="soil_moisture_back",
        display_name="soil moisture b",
        type=SensorType.SOIL_MOISTURE,
        unit=MeasureUnit,
        position=Position.BACK,
        pin=pin_back,
    )

    soil_moisture_sensor_back.setup()

    soil_moisture_sensor_front = SoilMoistureSensor(
        identifier="soil_moisture_front",
        display_name="soil moisture f",
        type=SensorType.SOIL_MOISTURE,
        unit=MeasureUnit,
        position=Position.FRONT,
        pin=pin_front,
    )

    soil_moisture_sensor_front.setup()

    return [soil_moisture_sensor_back, soil_moisture_sensor_front]


def setup_temperature_sensors(
    outside_sensor_id: str,
    inside_sensor_id: str,
    sensor_up: Optional[DHT11] = None,
) -> list[TemperatureSensor]:

    temperature_sensors = []

    temperature_sensors = W1ThermSensor.get_available_sensors()

    temperatureOutsideSensor = next(
        (sens for sens in temperature_sensors if sens.id == outside_sensor_id),
        None,
    )

    outside_sensor = TemperatureSensor(
        identifier="temperature_outside",
        display_name="temperature out",
        type=SensorType.TEMPERATURE,
        unit=MeasureUnit.CELSIUS,
        position=Position.OUTSIDE,
        sensor_obj=temperatureOutsideSensor,
    )

    temperature_sensors.append(outside_sensor)

    temperatureInsideSensor = next(
        (sens for sens in temperature_sensors if sens.id == inside_sensor_id),
        None,
    )

    inside_sensor = TemperatureSensor(
        identifier="temperature_inside",
        display_name="temperature in",
        type=SensorType.TEMPERATURE,
        unit=MeasureUnit.CELSIUS,
        position=Position.INSIDE,
        sensor_obj=temperatureInsideSensor,
    )

    temperature_sensors.append(inside_sensor)

    if sensor_up:
        temperature_sensors.append(
            TemperatureSensor(
                identifier="temperature_up",
                display_name="temperature up",
                type=SensorType.TEMPERATURE,
                unit=MeasureUnit.CELSIUS,
                position=Position.UP,
                sensor_obj=sensor_up,
            )
        )

    return temperature_sensors
