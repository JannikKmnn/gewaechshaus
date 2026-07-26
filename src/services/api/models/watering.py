from pydantic import BaseModel


class WateringRequestProperties(BaseModel):

    watering_time_seconds: float | None = None
