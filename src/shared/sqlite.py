import os

import aiosqlite

from aiosqlite import Connection
from datetime import datetime
from typing import Optional


async def setup_client() -> Connection | None:

    conn = aiosqlite.connect(database=os.getenv("SQLITE_DB_NAME"))

    return conn


async def setup_db(
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


async def get_window_events(
    sqlite_client: Connection,
    actuator_events_table: str,
    identifier: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    
    get_stmt = f"SELECT * FROM {actuator_events_table}"
    multiple_conditions = False

    if identifier:
        get_stmt += f" WHERE identifier={identifier}"
        multiple_conditions = True

    if start_time:
        get_stmt += f" {"WHERE" if not multiple_conditions else "AND"} timestamp >= {start_time.isoformat()}"
        multiple_conditions = True
    if end_time:
        get_stmt += f" {"WHERE" if not multiple_conditions else "AND"} timestamp <= {end_time.isoformat()}"
        multiple_conditions = True

    cursor = await sqlite_client.execute(get_stmt)
    rows = cursor.fetchall()

    return rows
