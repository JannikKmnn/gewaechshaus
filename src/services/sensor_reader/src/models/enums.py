from enum import Enum


class MQTTProperties(Enum):

    broker: str
    port: int
    user: str
    password: str
