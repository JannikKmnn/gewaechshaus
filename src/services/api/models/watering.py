from dataclasses import dataclass
from typing import Optional


@dataclass
class WateringRequestProperties:

    watering_time_seconds: float = None
