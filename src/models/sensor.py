import os

import bme280

from pydantic import BaseModel, ConfigDict, field_validator
from abc import ABC, abstractmethod

from typing import Literal, Optional
from src.models.enums import MeasureUnit, SensorType, Position
from src.utils.decorators import retry

from smbus2 import SMBus
from w1thermsensor import W1ThermSensor
import RPi.GPIO as GPIO  # type: ignore


class Sensor(ABC, BaseModel):

    identifier: str
    display_name: str
    type: SensorType
    unit: Optional[MeasureUnit] = None
    position: Optional[Position] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("display_name", mode="after")
    def validate(cls, v: str) -> str:
        num_lcd_columns = os.getenv("LCD_COLUMNS")
        if num_lcd_columns is None:
            num_lcd_columns = 16
        if len(v) > int(num_lcd_columns):
            raise ValueError("display name longer than lcd columns available.")
        return v

    @abstractmethod
    async def measure(self):
        pass


class BarometricSensor(Sensor):

    sensor_obj: SMBus
    bme280_params: bme280.params
    sensor_address: int

    @retry(times=3)
    async def measure(self) -> dict:

        data = bme280.sample(
            bus=self.sensor_obj,
            address=self.sensor_address,
            compensation_params=self.bme280_params,
        )

        position = self.position.value

        return {
            "temperature": {
                "value": data.temperature,
                "unit": MeasureUnit.CELSIUS.value,
                "identifier": f"temperature_{position}",
                "display_name": f"temperature {position}",
            },
            "humidity": {
                "value": data.humidity,
                "unit": MeasureUnit.PERCENT.value,
                "identifier": f"humidity_{position}",
                "display_name": f"humidity {position}",
            },
            "air_pressure": {
                "value": data.pressure,
                "unit": MeasureUnit.HECTOPASCAL.value,
                "identifier": f"air_pressure_{position}",
                "display_name": f"air pressure {position}",
            },
        }


class TemperatureSensor(Sensor):

    sensor_obj: W1ThermSensor

    @retry(times=3)
    async def measure(self) -> float:

        temperature_c = self.sensor_obj.get_temperature()

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
