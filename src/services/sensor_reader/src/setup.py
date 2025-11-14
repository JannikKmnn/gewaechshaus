from w1thermsensor import W1ThermSensor

from models.sensor import TemperatureSensor
from models.enums import Position, SensorType, MeasureUnit


def setup_temperature_sensors(
    outside_sensor_id: str,
    inside_sensor_id: str,
) -> list[TemperatureSensor]:

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

    return [outside_sensor, inside_sensor]
