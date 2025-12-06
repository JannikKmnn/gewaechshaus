import os
import asyncio

from logging import Logger

from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from dotenv import load_dotenv

load_dotenv()

logger = Logger(name="test_influxdb")


async def main():

    print(os.getenv("INFLUXDB_HOST"))
    print(os.getenv("INFLUXDB_ORG"))
    print(os.getenv("INFLUXDB_BUCKET"))

    client = InfluxDBClientAsync(
        url=os.getenv("INFLUXDB_HOST"),
        token=os.getenv("INFLUXDB_TOKEN"),
        org=os.getenv("INFLUXDB_ORG"),
        timeout=10000,
    )

    print(client)

    # test API


if __name__ == "__main__":
    asyncio.run(main())
