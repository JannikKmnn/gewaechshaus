from pydantic import BaseModel
from abc import ABC, abstractmethod

from typing import Optional
from enums import MeasureUnit, SensorType, Position


class Sensor(ABC, BaseModel):

    identifier: str
    type: SensorType
    unit: MeasureUnit
    position: Optional[Position] = None

    @abstractmethod
    async def measure(self):
        pass


class TemperatureSensor(Sensor):

    async def measure(self, sensor_obj):
        temperature_c = sensor_obj.get_temperature()
        return temperature_c
