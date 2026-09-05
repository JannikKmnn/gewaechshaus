from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Literal

from src.models.enums import SensorType

import numpy as np


@dataclass
class DataRequestProperties:

    start_time: datetime
    measurement: Optional[SensorType] = None
    end_time: Optional[datetime] = None


@dataclass
class DataResponseProperties:

    timestamps: list[datetime]
    sensor_identifier: list[str]
    values: np.ndarray


@dataclass
class SoilMoistureIntervalsRequestProperties:

    start_time: datetime
    end_time: datetime
    sensor_identifier: Literal["soil_moisture_back", "soil_moisture_front"]
