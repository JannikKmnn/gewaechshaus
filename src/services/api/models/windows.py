from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class WindowEventsRequestProperties:

    window_identifier: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class WindowConfigurationResponseProperties:

    window_identifier: str
    inside_temperature_opening_threshold: float


@dataclass
class WindowConfigurationUpdateProperties:

    window_position: str
    inside_temperature_opening_threshold: float
