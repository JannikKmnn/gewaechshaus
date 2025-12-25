import sqlite3

from datetime import datetime


async def setup_db(
    db_name: str,
    actuator_events_table: str,
):

    # creates DB if not exists already
    con = sqlite3.connect(database=db_name)
    cur = con.cursor()

    # creates table for actuator events
    sql_stmt = f"""CREATE TABLE IF NOT EXISTS
    {actuator_events_table}(identifier TEXT, timestamp DATETIME, status TINYINT)
    """

    cur.execute(sql_stmt)

    con.commit()
    con.close()


async def write_window_status_to_db(
    db_name: str,
    actuator_events_table: str,
    identifier: str,
    timestamp: datetime,
    opened: int,
):

    con = sqlite3.connect(database=db_name)
    cur = con.cursor()

    insert_stmt = f"INSERT INTO {actuator_events_table} VALUES (?, ?, ?)"

    cur.execute(insert_stmt, (identifier, timestamp.isoformat(), opened))

    con.commit()
    con.close()
