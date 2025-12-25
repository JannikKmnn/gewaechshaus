import sqlite3


async def setup_db(
    db_name: str,
    actuator_events_table: str,
):

    # creates DB if not exists already
    con = sqlite3.connect(database=db_name)
    cur = con.cursor()

    # creates table for actuator events
    sql_stmt = f"""CREATE TABLE IF NOT EXISTS
    {actuator_events_table}(identifier TEXT, timestamp DATETIME, status BOOLEAN)
    """

    cur.execute(sql_stmt)
