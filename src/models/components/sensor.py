import os

import bme280

from pydantic import field_validator
from abc import abstractmethod

from typing import Optional
from src.models.components.base import Component
from src.models.data import Measurement
from src.models.enums import MeasureUnit, SensorType
from src.utils.decorators import retry

from smbus2 import SMBus
from w1thermsensor import W1ThermSensor
import RPi.GPIO as GPIO  # type: ignore


class Sensor(Component):

    display_name: str
    type: SensorType
    unit: Optional[MeasureUnit] = None

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
    async def measure(self) -> list[Measurement]:

        data = bme280.sample(
            bus=self.sensor_obj,
            address=self.sensor_address,
            compensation_params=self.bme280_params,
        )

        return [
            Measurement(
                identifier=f"temperature_{self.position.value.lower()}",
                value=round(data.temperature, 2),
                unit=MeasureUnit.CELSIUS,
                type=SensorType.TEMPERATURE,
                display_name=f"temperature {self.position.value.lower()}",
            ),
            Measurement(
                identifier="humidity",
                value=int(data.humidity),
                unit=MeasureUnit.PERCENT,
                type=SensorType.HUMIDITY,
                display_name="humidity",
            ),
            Measurement(
                identifier="air_pressure",
                value=round(data.pressure, 2),
                unit=MeasureUnit.HECTOPASCAL,
                type=SensorType.AIR_PRESSURE,
                display_name="air pressure",
            ),
        ]


class TemperatureSensor(Sensor):

    sensor_obj: W1ThermSensor

    @retry(times=3)
    async def measure(self) -> list[Measurement]:

        temperature_c = self.sensor_obj.get_temperature()

        return [
            Measurement(
                identifier=self.identifier,
                value=temperature_c,
                unit=MeasureUnit.CELSIUS,
                type=self.type,
                display_name=self.display_name,
            ),
        ]


class SoilMoistureSensor(Sensor):

    pin: int

    def setup(self) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

    @retry(times=2)
    async def measure(self) -> list[Measurement]:

        value = GPIO.input(self.pin)
        is_wet = value == GPIO.LOW
        result = "wet" if is_wet else "dry"

        return [
            Measurement(
                identifier=self.identifier,
                value=result,
                type=self.type,
                display_name=self.display_name,
                unit=None,
            )
        ]
