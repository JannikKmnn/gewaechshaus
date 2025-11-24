import os

from datetime import datetime, timezone
from fastapi import Depends
from typing import Literal

from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from src.shared.influxdb import setup_client

async def get_measurements(
    start_time: datetime,
    measurement: Literal["AirPressure", "Humidity", "SoilMoisture", "Temperature"],
    end_time: datetime = datetime.now(tz=timezone.utc),
    influxdb_client: InfluxDBClientAsync = Depends(setup_client),
):
    
    query = f"""
        SELECT *
        FROM
    """
