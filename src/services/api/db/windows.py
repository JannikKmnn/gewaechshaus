from datetime import datetime
from typing import Optional

from src.shared.sqlite import setup_client


async def get_window_events(
    actuator_events_table: str,
    identifier: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):

    sqlite_client = await setup_client()

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

    async with sqlite_client:
        cursor = await sqlite_client.execute(get_stmt)
        rows = cursor.fetchall()

        await sqlite_client.commit()
        await sqlite_client.close()

    return rows
