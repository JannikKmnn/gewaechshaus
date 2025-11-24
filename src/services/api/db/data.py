import os

from datetime import datetime, timezone
from fastapi import Depends
from typing import Literal, Optional

from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from src.shared.influxdb import setup_client

async def get_measurements(
    start_time: datetime,
    measurement: Literal["AirPressure", "Humidity", "SoilMoisture", "Temperature"],
    end_time: datetime = datetime.now(tz=timezone.utc),
    influxdb_client: InfluxDBClientAsync = Depends(setup_client),
    field_identifer: Optional[str] = None,
):
    
    query = f"""
        SELECT *
        FROM {measurement}
        WHERE time >= {str(start_time)} AND time <= {str(end_time)}
        AND ({field_identifer} IS NOT NULL)
    """

    async with influxdb_client:
        table = await influxdb_client.query_api().query(
            query=query
        )