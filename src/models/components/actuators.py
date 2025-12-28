import asyncio
import aiosqlite

from datetime import datetime, timezone

from src.models.components.base import Component
from src.models.exceptions import StateAlreadyReached, EventRecordFailed
from src.shared.sqlite import write_window_status_to_db

import RPi.GPIO as GPIO  # type: ignore


class LinearActuator(Component):

    extend_pin: int
    retract_pin: int
    moving_time_seconds: float

    last_extension: datetime = datetime(2025, 12, 1, tzinfo=timezone.utc)
    last_retraction: datetime = datetime(2025, 12, 2, tzinfo=timezone.utc)

    is_extended: bool = False

    # sqlite properties for event storing
    sqlite_db_name: str
    sqlite_events_table: str

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
        await asyncio.sleep(delay=self.moving_time_seconds)
        GPIO.output(self.extend_pin, False)

        self.is_extended = True

        timestamp = datetime.now(tz=timezone.utc).replace(microsecond=0)
        self.last_extension = timestamp

        try:
            async with aiosqlite.connect(database=self.sqlite_db_name) as db:
                _ = await write_window_status_to_db(
                    sqlite_client=db,
                    actuator_events_table=self.sqlite_events_table,
                    identifier=self.identifier,
                    timestamp=timestamp,
                    opened=1,
                )
                await db.close()
        except Exception as err:
            raise EventRecordFailed(
                f"Storing extension event in DB failed for window {self.position.value} due to {err}"
            )

    async def retract(self) -> None:

        if not self.is_extended:
            raise StateAlreadyReached(f"Actuator {self.identifier} already retracted.")

        GPIO.output(self.extend_pin, False)
        GPIO.output(self.retract_pin, True)
        await asyncio.sleep(delay=self.moving_time_seconds)
        GPIO.output(self.retract_pin, False)

        self.is_extended = False

        timestamp = datetime.now(tz=timezone.utc).replace(microsecond=0)
        self.last_retraction = timestamp

        try:
            async with aiosqlite.connect(database=self.sqlite_db_name) as db:
                _ = await write_window_status_to_db(
                    sqlite_client=db,
                    actuator_events_table=self.sqlite_events_table,
                    identifier=self.identifier,
                    timestamp=timestamp,
                    opened=0,
                )
                await db.close()
        except Exception as err:
            raise EventRecordFailed(
                f"Storing retraction event in DB failed for window {self.position.value} due to {err}"
            )
