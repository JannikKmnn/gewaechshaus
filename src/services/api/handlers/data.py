from fastapi import HTTPException

from typing import Optional

from src.services.api.models.data import DataRequestProperties
from src.services.api.db.data import get_measurements as get_db_measurements


async def get_measurements(
    req_properties: DataRequestProperties, sensor_identifier: Optional[str] = None
) -> list[dict]:

    if req_properties.end_time <= req_properties.start_time:
        raise HTTPException(
            status_code=400, detail="Query end time must be after start time."
        )

    values = await get_db_measurements(
        start_time=req_properties.start_time,
        measurement=req_properties.measurement,
        end_time=req_properties.end_time,
        field_identifier=[sensor_identifier] if sensor_identifier else None,
    )

    return [
        {
            "measurement": val[0],
            "field": val[1],
            "timestamp": val[2],
            "value": val[3],
        }
        for val in values
    ]
