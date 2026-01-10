from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from src.models.enums import SensorType

import numpy as np


@dataclass
class WindowEventsRequestProperties:

    window_identifier: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


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
