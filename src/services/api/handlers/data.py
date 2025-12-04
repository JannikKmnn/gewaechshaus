from typing import Optional

from src.services.api.models.data import DataRequestProperties
from src.services.api.db.data import get_measurements as get_db_measurements


async def get_measurements(
    req_properties: DataRequestProperties, sensor_identifier: Optional[str] = None
):

    values = await get_db_measurements(
        start_time=req_properties.start_time,
        measurement=req_properties.measurement,
        end_time=req_properties.end_time,
        field_identifier=[sensor_identifier] if sensor_identifier else None,
    )

    return values
