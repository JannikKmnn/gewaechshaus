from dataclasses import dataclass

from typing import Optional

from src.models.enums import MeasureUnit, SensorType


@dataclass
class Measurement:

    identifier: str
    value: float | int | str
    display_name: str
    type: SensorType
    unit: Optional[MeasureUnit] = None
