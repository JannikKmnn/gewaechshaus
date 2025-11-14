from pydantic import BaseModel
from abc import ABC, abstractmethod
from logging import Logger

from typing import Literal, Optional, Union
from enums import MeasureUnit, SensorType, Position
from decorators import retry

from adafruit_dht import DHT11
from w1thermsensor import W1ThermSensor
import RPi.GPIO as GPIO  # type: ignore


class Sensor(ABC, BaseModel):

    identifier: str
    display_name: str
    type: SensorType
    unit: Optional[MeasureUnit] = None
    position: Optional[Position] = None
    logger: Optional[Logger] = None

    @abstractmethod
    async def measure(self):
        pass


class TemperatureSensor(Sensor):

    sensor_obj: Union[W1ThermSensor, DHT11]

    @retry(times=3)
    async def measure(self):

        if isinstance(self.sensor_obj, W1ThermSensor):
            temperature_c = self.sensor_obj.get_temperature()
        elif isinstance(self.sensor_obj, DHT11):
            temperature_c = self.sensor_obj.temperature

        return temperature_c


class SoilMoistureSensor(Sensor):

    pin: int

    @retry(times=2)
    async def measure(self) -> Literal["wet", "dry"]:

        value = GPIO.input(self.pin)
        is_wet = value == GPIO.LOW

        return "wet" if is_wet else "dry"


class HumiditySensor(Sensor):

    sensor_obj: DHT11

    @retry(times=2)
    async def measure(self) -> float:

        humidity = self.sensor_obj.humidity
        return humidity
