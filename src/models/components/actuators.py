import asyncio

from base import Component
from src.models.exceptions import StateAlreadyReached

import RPi.GPIO as GPIO  # type: ignore


class LinearActuator(Component):

    extend_pin: int
    retract_pin: int
    moving_time_seconds: float

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

        GPIO.output(self.extend_pin, True)
        asyncio.sleep(delay=self.moving_time_seconds)
        GPIO.output(self.extend_pin, False)

        self.is_extended = True

    async def retract(self) -> None:

        if not self.is_extended:
            raise StateAlreadyReached(f"Actuator {self.identifier} already retracted.")

        GPIO.output(self.retract_pin, True)
        asyncio.sleep(delay=self.moving_time_seconds)
        GPIO.output(self.retract_pin, False)

        self.is_extended = False
