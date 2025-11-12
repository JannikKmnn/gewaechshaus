from pydantic import BaseModel

from enums import MeasureUnit, SensorType

class Sensor(BaseModel):

    identifier: str
    type: SensorType
    unit: MeasureUnit