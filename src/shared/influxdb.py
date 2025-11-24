import os

from logging import Logger

from influxdb_client import Point
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from src.models.data import Measurement
from src.models.influxdb import InfluxDBProperties
from src.models.enums import InfluxDBResponse


def setup_influxdb_client(
    influxdb_properties: InfluxDBProperties,
    logger: Logger,
) -> InfluxDBClientAsync | None:
    try:
        client = InfluxDBClientAsync(
            url=influxdb_properties.host,
            token=influxdb_properties.token,
            org=influxdb_properties.org,
            timeout=influxdb_properties.timeout,
        )
    except Exception as err:
        logger.warning(f"Influxdb setup failed due to: {err}")
        client = None

    return client


async def setup_client():

    properties = InfluxDBProperties(
        host=os.getenv("INFLUXDB_HOST"),
        org=os.getenv("INFLUXDB_ORG"),
        token=os.getenv("INFLUXDB_TOKEN")
    )

    client = setup_influxdb_client(influxdb_properties=properties)

    return client


async def write_to_influxdb(
    client: InfluxDBClientAsync,
    bucket: str,
    measurement_results: list[Measurement],
    logger: Logger,
) -> InfluxDBResponse:

    records = [
        Point(measurement_name=rec.type.value).field(
            field=rec.identifier, value=rec.value
        )
        for rec in measurement_results
    ]

    try:
        _ = await client.write_api().write(
            bucket=bucket,
            record=records,
        )
        return InfluxDBResponse.SUCCESS
    except Exception as err:
        logger.warning(f"Inserting DB data failed due to: {err}")
        return InfluxDBResponse.ERROR
