from src.shared.sqlite import setup_client


async def upgrade() -> None:

    sqlite_client = await setup_client()

    # creates table for windows
    create_stmt = """CREATE TABLE IF NOT EXISTS window (
    identifier TEXT PRIMARY KEY,
    temperature_threshold_open INTEGER
    );
    """

    insert_stmt = f"""INSERT OR IGNORE 
    INTO window(identifier, temperature_threshold_open) 
    VALUES (?, ?)"""

    async with sqlite_client:
        await sqlite_client.execute("BEGIN")

        # 1. create table
        await sqlite_client.execute(create_stmt)

        # 2. Add data points
        await sqlite_client.execute(insert_stmt, ("linear_actuator_left", 20))
        await sqlite_client.execute(insert_stmt, ("linear_actuator_right", 22))
        await sqlite_client.commit()


async def downgrade() -> None:

    sqlite_client = await setup_client()

    # deletes table again
    delete_stmt = "DROP TABLE IF EXISTS window"

    async with sqlite_client:
        await sqlite_client.execute("BEGIN")

        await sqlite_client.execute(delete_stmt)
        await sqlite_client.commit()
