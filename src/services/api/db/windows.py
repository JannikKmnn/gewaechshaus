from datetime import datetime
from typing import Optional, Literal

from src.services.api.models.windows import WindowConfigurationUpdateProperties
from src.shared.sqlite import setup_client


async def get_window_events(
    actuator_events_table: str,
    identifier: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):

    sqlite_client = await setup_client()

    sql = f"SELECT * FROM {actuator_events_table}"
    conditions = []
    params = []

    if identifier:
        conditions.append("identifier = ?")
        params.append(identifier)

    if start_time:
        conditions.append("timestamp >= ?")
        params.append(start_time.isoformat())

    if end_time:
        conditions.append("timestamp <= ?")
        params.append(end_time.isoformat())

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    async with sqlite_client:
        cursor = await sqlite_client.execute(sql, params)
        rows = await cursor.fetchall()

        await sqlite_client.commit()
        await sqlite_client.close()

    return rows


async def get_nearest_window_event(
    actuator_events_table: str,
    identifier: str,
    target_time: datetime,
    mode: Literal["before", "after"],
):
    sqlite_client = await setup_client()

    timestamp_operator = "<=" if mode == "before" else ">="
    order = "ASC" if mode == "after" else "DESC"

    sql = f"""
        SELECT * FROM {actuator_events_table}
        WHERE identifier = ? AND timestamp {timestamp_operator} ?
        ORDER BY timestamp {order}
        LIMIT 1
    """

    async with sqlite_client:
        cursor = await sqlite_client.execute(sql, [identifier, target_time.isoformat()])
        row = await cursor.fetchone()

        await sqlite_client.commit()
        await sqlite_client.close()

    return row


async def get_window_configurations(
    identifier: str,
    window_entity_table: str,
):

    sqlite_client = await setup_client()

    sql = f"SELECT * FROM {window_entity_table} WHERE identifier = ?"

    async with sqlite_client:
        cursor = await sqlite_client.execute(sql, [identifier])
        row = await cursor.fetchone()

        await sqlite_client.commit()
        await sqlite_client.close()

    return row


async def update_window_configurations(
    identifier: str,
    window_entity_table: str,
    updates: WindowConfigurationUpdateProperties,
):
    sqlite_client = await setup_client()

    sql = f"UPDATE {window_entity_table} SET temperature_threshold_open=? WHERE identifier = ?"

    async with sqlite_client:

        await sqlite_client.execute(
            sql,
            [
                updates.inside_temperature_opening_threshold,
                identifier,
            ],
        )

        await sqlite_client.commit()
        await sqlite_client.close()
