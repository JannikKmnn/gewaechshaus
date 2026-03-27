from datetime import datetime
from dataclasses import dataclass, asdict
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

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}
