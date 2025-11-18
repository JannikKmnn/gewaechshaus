from dataclasses import dataclass


@dataclass
class InfluxDBProperties:

    host: str
    org: str
    token: str
    timeout: int
