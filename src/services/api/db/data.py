from datetime import datetime, timezone
from typing import Optional

from src.models.enums import SensorType
from src.models.exceptions import QueryError
from src.shared.influxdb import setup_client


async def fetch_measurements(
    start_time: datetime,
    measurement: Optional[SensorType] = None,
    end_time: Optional[datetime] = None,
    field_identifier: Optional[list[str]] = None,
    aggregation: Optional[str] = None,
    binary_state_changes_identifier: Optional[str] = None,
) -> list[list]:

    influxdb_client = await setup_client()

    if end_time is None:
        end_time = datetime.now(tz=timezone.utc)

    query = f"""
    from(bucket:"greenhouse")
        |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
    """

    if measurement is not None:
        query += (
            f"""    |> filter(fn: (r) => r["_measurement"] == "{measurement.value}")"""
        )

    if field_identifier is not None:
        filters = " or ".join(
            [f'r["_field"] == "{ident}"' for ident in field_identifier]
        )
        query += f"""    |> filter(fn: (r) => {filters})"""

    if aggregation is not None:
        query += f"""    |> aggregateWindow(every: {aggregation}, fn: mean)"""

    if binary_state_changes_identifier is not None:
        if field_identifier is None or len(field_identifier) != 1:
            raise QueryError(
                f"State changes can only be fetched for a single field identifier, got {field_identifier}."
            )
        if aggregation is not None:
            raise QueryError(
                f"State changes cannot be fetched when aggregation is specified, got {aggregation}."
            )

        query += f"""    
            |> map(fn: (r) => ({{r with state_value: if r._value == "{binary_state_changes_identifier}" then 1 else 0}}))
            |> difference(columns: ["state_value"])
            |> filter(fn: (r) => r.state_value != 0)
        """

    async with influxdb_client:
        table = await influxdb_client.query_api().query(query=query)

    columns = ["_measurement", "_field", "_time", "_value"]
    result = table.to_values(columns=columns)
    return result
