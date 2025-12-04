from datetime import datetime, timezone
from fastapi import Depends
from typing import Literal, Optional

from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from src.shared.influxdb import setup_client


async def get_measurements(
    start_time: datetime,
    measurement: Optional[
        Literal["AirPressure", "Humidity", "SoilMoisture", "Temperature"]
    ] = None,
    end_time: Optional[list[str]] = None,
    field_identifier: Optional[list[str]] = None,
    influxdb_client: InfluxDBClientAsync = Depends(setup_client),
) -> list[list]:

    if end_time is None:
        end_time = datetime.now(tz=timezone.utc)

    query = f"""
    from(bucket:"greenhouse")
        |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
    """

    if measurement:
        query += f"""    |> filter(fn: (r) => r["_measurement"] == "{measurement}")"""

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
