from datetime import datetime
from dataclasses import dataclass
from typing import Union

import numpy as np


@dataclass
class DataRequestProperties:

    start_time: Union[datetime, None] = None
    end_time: Union[datetime, None] = None


@dataclass
class DataResponseProperties:

    timestamps: list[datetime]
    sensor_identifier: list[str]
    values: np.ndarray
