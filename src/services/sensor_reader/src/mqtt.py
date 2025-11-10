import paho.mqtt.client as mqtt
import json

from datetime import datetime, timezone
from logging import Logger

from models.enums import MQTTProperties


def setup_client(
    broker: str,
    port: int,
    user: str,
    password: str,
    logger: Logger,
    start_loop: bool = True,
) -> mqtt.Client | None:

    client = mqtt.Client()
    client.username_pw_set(username=user, password=password)
    try:
        client.tls_set()
        client.connect(host=broker, port=port)
        if start_loop:
            client.loop_start()
        return client
    except Exception as err:
        logger.warning(f"Mqtt connection/loop start failed due to: {err}")
        return None


async def publish_message(client: mqtt.Client, result_dict: dict):

    result_dict["timestamp"] = str(datetime.now(tz=timezone.utc).replace(second=0))

    payload = json.dumps(result_dict)

    if client is None:
        return

    client.publish("greenhouse/sensors", payload=payload, qos=1)
