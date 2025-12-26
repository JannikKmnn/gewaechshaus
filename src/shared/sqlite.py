import aiosqlite

from aiosqlite import Connection
from datetime import datetime


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
