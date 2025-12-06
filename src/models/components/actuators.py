import asyncio

from datetime import datetime, timezone

from src.models.components.base import Component
from src.models.exceptions import StateAlreadyReached

import RPi.GPIO as GPIO  # type: ignore


class LinearActuator(Component):

    extend_pin: int
    retract_pin: int
    moving_time_seconds: float

    last_extension: datetime = datetime(2025, 12, 1, tzinfo=timezone.utc)
    last_retraction: datetime = datetime(2025, 12, 2, tzinfo=timezone.utc)

    is_extended: bool = False

    def setup(self) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.extend_pin, GPIO.OUT)
        GPIO.setup(self.retract_pin, GPIO.OUT)
        GPIO.output(self.extend_pin, False)
        GPIO.output(self.retract_pin, False)

    async def extend(self) -> None:

        if self.is_extended:
            raise StateAlreadyReached(f"Actuator {self.identifier} already extended.")

        GPIO.output(self.retract_pin, False)
        GPIO.output(self.extend_pin, True)
        asyncio.sleep(delay=self.moving_time_seconds)
        GPIO.output(self.extend_pin, False)

        self.is_extended = True
        self.last_extension = datetime.now(tz=timezone.utc)

    async def retract(self) -> None:

        if not self.is_extended:
            raise StateAlreadyReached(f"Actuator {self.identifier} already retracted.")

        GPIO.output(self.extend_pin, False)
        GPIO.output(self.retract_pin, True)
        asyncio.sleep(delay=self.moving_time_seconds)
        GPIO.output(self.retract_pin, False)

        self.is_extended = False
        self.last_retraction = datetime.now(tz=timezone.utc)
