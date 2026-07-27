from pydantic import BaseModel

from datetime import datetime


class WateringRequestProperties(BaseModel):

    watering_time_seconds: float | None = None


class WateringEventsRequestProperties(BaseModel):

    start_time: datetime | None = None
    end_time: datetime | None = None
