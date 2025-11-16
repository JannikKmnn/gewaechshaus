import paho.mqtt.client as mqtt
import json

from datetime import datetime, timezone
from logging import Logger

from src.models.mqtt import MQTTProperties
from src.models.enums import MQTTResponse


def setup_client(
    client_properties: MQTTProperties,
    logger: Logger,
    start_loop: bool = True,
) -> mqtt.Client | None:

    client = mqtt.Client()
    client.username_pw_set(
        username=client_properties.user, password=client_properties.password
    )
    try:
        client.tls_set()
        client.connect(host=client_properties.broker, port=client_properties.port)
        if start_loop:
            client.loop_start()
        return client
    except Exception as err:
        logger.warning(f"Mqtt connection/loop start failed due to: {err}")
        return None


async def publish_message(
    client: mqtt.Client, result_dict: dict, logger: Logger
) -> MQTTResponse:

    timestamp = datetime.now(tz=timezone.utc).replace(microsecond=0)
    result_dict["timestamp"] = str(timestamp)

    payload = json.dumps(result_dict)

    if client is None:
        return MQTTResponse.NO_CLIENT

    try:
        client.publish("greenhouse/sensors", payload=payload, qos=1)
        return MQTTResponse.SUCCESS
    except Exception as err:
        logger.warning(f"Message on {timestamp} could not be published due to: {err}")
        return MQTTResponse.CLIENT_CRASHED
