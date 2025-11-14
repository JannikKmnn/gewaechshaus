import os

from pydantic import BaseModel, field_validator
from abc import ABC, abstractmethod
from logging import Logger

from typing import Literal, Optional, Union
from enums import MeasureUnit, SensorType, Position
from utils.decorators import retry

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

    @field_validator("display_name", mode="after")
    def validate(cls, v: str) -> str:
        num_lcd_columns = os.getenv("LCD_COLUMNS")
        if num_lcd_columns is None:
            raise KeyError("Max Number of LCD columns not findable as env variable.")
        if len(v) > int(num_lcd_columns):
            raise ValueError("display name longer than lcd columns available.")
        return v

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

    def setup(self) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

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
