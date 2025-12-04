from datetime import datetime
from dataclasses import dataclass
from typing import Union

import numpy as np


@dataclass
class DataRequestProperties:

    measurement: str
    start_time: datetime
    end_time: Union[datetime, None] = None


@dataclass
class DataResponseProperties:

    timestamps: list[datetime]
    sensor_identifier: list[str]
    values: np.ndarray
