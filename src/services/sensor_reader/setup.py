import bme280

from logging import Logger

from w1thermsensor import W1ThermSensor
from RPLCD.i2c import CharLCD
from smbus2 import SMBus

from src.shared.influxdb import setup_influxdb_client

from src.models.enums import Position, SensorType, MeasureUnit
from src.models.influxdb import InfluxDBProperties
from src.models.components.actuators import LinearActuator
from src.models.components.sensor import (
    BarometricSensor,
    TemperatureSensor,
    SoilMoistureSensor,
)


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


def setup_influxdb(
    host: str,
    org: str,
    token: str,
    timeout: int,
    logger: Logger,
):

    influxdb_properties = InfluxDBProperties(
        host=host,
        org=org,
        token=token,
        timeout=timeout,
    )

    influxdb_client = setup_influxdb_client(
        influxdb_properties=influxdb_properties, logger=logger
    )

    return influxdb_client


def setup_barometric_sensor(
    i2c_address: int,
    i2c_port: int,
) -> BarometricSensor:

    bus = SMBus(i2c_port)
    params = bme280.load_calibration_params(
        bus=bus,
        address=i2c_address,
    )

    barometric_sensor = BarometricSensor(
        identifier="barometric_up",
        display_name="barometric up",
        type=SensorType.BAROMETRIC,
        position=Position.UP,
        sensor_obj=bus,
        bme280_params=params,
        sensor_address=i2c_address,
    )

    return barometric_sensor


def setup_soil_moisture_sensors(
    pin_back: int,
    pin_front: int,
) -> list[SoilMoistureSensor]:

    soil_moisture_sensor_back = SoilMoistureSensor(
        identifier="soil_moisture_back",
        display_name="soil moisture b",
        type=SensorType.SOIL_MOISTURE,
        position=Position.BACK,
        pin=pin_back,
    )

    soil_moisture_sensor_back.setup()

    soil_moisture_sensor_front = SoilMoistureSensor(
        identifier="soil_moisture_front",
        display_name="soil moisture f",
        type=SensorType.SOIL_MOISTURE,
        position=Position.FRONT,
        pin=pin_front,
    )

    soil_moisture_sensor_front.setup()

    return [soil_moisture_sensor_back, soil_moisture_sensor_front]


def setup_temperature_sensors(
    outside_sensor_id: str,
    inside_sensor_id: str,
) -> list[TemperatureSensor]:

    temperature_sensors_return = []

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

    temperature_sensors_return.append(outside_sensor)

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

    temperature_sensors_return.append(inside_sensor)

    return temperature_sensors_return
