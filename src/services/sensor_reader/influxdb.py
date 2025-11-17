from logging import Logger

from influxdb_client import Point
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from src.models.influxdb import InfluxDBProperties
from src.models.enums import InfluxDBResponse
from src.models.sensor import Sensor


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


async def write_to_influxdb(
    client: InfluxDBClientAsync,
    bucket: str,
    result_dict: dict,
    sensors: list[Sensor],
    logger: Logger,
) -> InfluxDBResponse:

    records = []
    for key, value in result_dict.items():
        if key == "timestamp":
            continue
        sensor = next((s for s in sensors if s.identifier == key), None)
        if sensor is None:
            logger.warning(
                f"Sensor not found with identifier {key} in sensors {sensors}"
            )
            continue
        records.append(
            Point(measurement_name=sensor.type.value)
            .tag(
                key="position",
                value=sensor.position.value if sensor.position else "unknown",
            )
            .field(field=sensor.identifier, value=value)
        )

    try:
        async with client:
            _ = await client.write_api().write(
                bucket=bucket,
                record=records,
            )
        return InfluxDBResponse.SUCCESS
    except Exception as err:
        logger.warning(f"Inserting DB data failed due to: {err}")
        return InfluxDBResponse.ERROR
