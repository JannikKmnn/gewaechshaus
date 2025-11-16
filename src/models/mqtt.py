from dataclasses import dataclass


@dataclass
class MQTTProperties:

    broker: str
    port: int
    user: str
    password: str
