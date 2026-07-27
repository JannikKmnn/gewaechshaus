import os

import aiosqlite

from aiosqlite import Connection
from datetime import datetime


async def setup_client() -> Connection | None:

    conn = aiosqlite.connect(database=os.getenv("SQLITE_DB_NAME"))

    return conn


async def setup_windows_db(
    db_name: str,
    actuator_events_table: str,
):

    # creates DB if not exists already
    sqlite_client = aiosqlite.connect(database=db_name)

    async with sqlite_client:

        # creates table for actuator events
        sql_stmt = f"""CREATE TABLE IF NOT EXISTS
        {actuator_events_table}(identifier TEXT, timestamp DATETIME, status TINYINT)
        """

        await sqlite_client.execute(sql_stmt)

        await sqlite_client.commit()
        await sqlite_client.close()


async def write_window_status_to_db(
    sqlite_client: Connection,
    actuator_events_table: str,
    identifier: str,
    timestamp: datetime,
    opened: int,
):

    insert_stmt = f"INSERT INTO {actuator_events_table} VALUES (?, ?, ?)"

    await sqlite_client.execute(
        insert_stmt, (identifier, timestamp.isoformat(), opened)
    )
    await sqlite_client.commit()


async def fetch_latest_window_events(
    sqlite_db_name: str,
    actuator_events_table: str,
    identifier: str,
):

    fetch_stmt = f"""
        SELECT * FROM {actuator_events_table}
        WHERE identifier = ?
        ORDER BY timestamp DESC LIMIT 2
    """

    async with aiosqlite.connect(database=sqlite_db_name) as db:
        cursor = await db.execute(fetch_stmt, (identifier,))
        rows = await cursor.fetchall()

        await db.commit()
        await db.close()

    return rows


async def setup_watering_db(
    db_name: str,
    watering_events_table: str,
):

    # creates DB if not exists already
    sqlite_client = aiosqlite.connect(database=db_name)

    async with sqlite_client:

        # creates table for watering events
        sql_stmt = f"""CREATE TABLE IF NOT EXISTS
        {watering_events_table}(timestamp DATETIME, duration_seconds INTEGER)
        """

        await sqlite_client.execute(sql_stmt)

        await sqlite_client.commit()
        await sqlite_client.close()


async def write_watering_event_to_db(
    sqlite_client: Connection,
    watering_events_table: str,
    timestamp: datetime,
    duration_seconds: int,
):

    insert_stmt = f"INSERT INTO {watering_events_table} VALUES (?, ?)"

    await sqlite_client.execute(insert_stmt, (timestamp.isoformat(), duration_seconds))
    await sqlite_client.commit()


async def fetch_latest_watering_events(
    sqlite_db_name: str,
    watering_events_table: str,
):

    fetch_stmt = f"""
        SELECT * FROM {watering_events_table}
        ORDER BY timestamp DESC LIMIT 2
    """

    async with aiosqlite.connect(database=sqlite_db_name) as db:
        cursor = await db.execute(fetch_stmt)
        rows = await cursor.fetchall()

        await db.commit()
        await db.close()

    return rows
