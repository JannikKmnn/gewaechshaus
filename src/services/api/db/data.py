from datetime import datetime, timezone
from typing import Optional

from src.models.enums import SensorType
from src.shared.influxdb import setup_client


async def get_measurements(
    start_time: datetime,
    measurement: Optional[SensorType] = None,
    end_time: Optional[list[str]] = None,
    field_identifier: Optional[list[str]] = None,
) -> list[list]:

    influxdb_client = await setup_client()

    if end_time is None:
        end_time = datetime.now(tz=timezone.utc)

    query = f"""
    from(bucket:"greenhouse")
        |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
    """

    if measurement:
        query += (
            f"""    |> filter(fn: (r) => r["_measurement"] == "{measurement.value}")"""
        )

    if field_identifier:
        filters = " or ".join(
            [f'r["_field"] == "{ident}"' for ident in field_identifier]
        )
        query += f"""    |> filter(fn: (r) => {filters})"""

    async with influxdb_client:
        table = await influxdb_client.query_api().query(query=query)

    columns = ["_measurement", "_field", "_time", "_value"]
    result = table.to_values(columns=columns)
    return result
