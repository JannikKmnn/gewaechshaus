import paho.mqtt.client as mqtt

import json

from datetime import datetime, timezone
from logging import Logger


def setup_client(
    mqtt_user: str,
    mqtt_pw: str,
    mqtt_host: str,
    mqtt_port: int,
    logger: Logger,
    start_loop: bool = True,
) -> mqtt.Client | None:

    client = mqtt.Client()
    client.username_pw_set(username=mqtt_user, password=mqtt_pw)
    try:
        client.tls_set()
        client.connect(host=mqtt_host, port=mqtt_port)
        if start_loop:
            client.loop_start()
        return client
    except Exception as err:
        logger.warning(f"Mqtt connection/loop start failed due to: {err}")
        return None


async def publish_message(client: mqtt.Client, result_dict: dict):

    result_dict["timestamp"] = datetime.now(tz=timezone.utc).replace(second=0)

    payload = json.dumps(result_dict)
    client.publish("greenhouse/sensors", payload=payload, qos=1)
