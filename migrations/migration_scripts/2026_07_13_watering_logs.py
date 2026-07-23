from src.shared.sqlite import setup_client


async def upgrade() -> None:

    sqlite_client = await setup_client()

    # creates table for windows
    create_stmt = """CREATE TABLE IF NOT EXISTS watering (
    timestamp DATETIME PRIMARY KEY,
    duration INTEGER
    );
    """

    async with sqlite_client:
        await sqlite_client.execute("BEGIN")

        # create table
        await sqlite_client.execute(create_stmt)
        await sqlite_client.commit()


async def downgrade() -> None:

    sqlite_client = await setup_client()

    # deletes table again
    delete_stmt = "DROP TABLE IF EXISTS watering"

    async with sqlite_client:
        await sqlite_client.execute("BEGIN")

        await sqlite_client.execute(delete_stmt)
        await sqlite_client.commit()
