import asyncio
import aiosqlite

from datetime import datetime, timedelta, timezone

from src.models.components.base import Component
from src.models.exceptions import (
    StateAlreadyReached,
    EventRecordFailed,
    StateFetchingFailed,
    WateringEventFetchingFailed,
)
from src.shared.sqlite import (
    write_window_status_to_db,
    fetch_latest_window_events,
    write_watering_event_to_db,
    fetch_latest_watering_events,
)

import RPi.GPIO as GPIO  # type: ignore


class Actuator(Component):

    # sqlite properties for event storing
    sqlite_db_name: str
    sqlite_events_table: str


class LinearActuator(Actuator):

    extend_pin: int
    retract_pin: int
    moving_time_seconds: float

    last_extension: datetime = datetime(2025, 12, 1, tzinfo=timezone.utc)
    last_retraction: datetime = datetime(2025, 12, 2, tzinfo=timezone.utc)

    is_extended: bool = False

    async def setup(self):

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.extend_pin, GPIO.OUT)
        GPIO.setup(self.retract_pin, GPIO.OUT)
        GPIO.output(self.extend_pin, False)
        GPIO.output(self.retract_pin, False)

        # fetch sqlite latest states (SSOT)

        try:
            latest_window_events = await fetch_latest_window_events(
                sqlite_db_name=self.sqlite_db_name,
                actuator_events_table=self.sqlite_events_table,
                identifier=self.identifier,
            )
        except Exception as err:
            raise StateFetchingFailed(
                f"Fetching window events from DB failed for window {self.position.value} due to {err}"
            )

        last_open_row: datetime = next(ev for ev in latest_window_events if ev[2] == 1)
        last_closing_row: datetime = next(
            ev for ev in latest_window_events if ev[2] == 0
        )

        self.last_extension: datetime = datetime.fromisoformat(
            last_open_row[1]
        ).replace(tzinfo=timezone.utc)
        self.last_retraction: datetime = datetime.fromisoformat(
            last_closing_row[1]
        ).replace(tzinfo=timezone.utc)

        if self.last_retraction < self.last_extension:
            self.is_extended = True

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


class WaterPump(Actuator):

    pin: int
    watering_time_seconds: float

    last_watering: datetime = datetime(2026, 7, 15, tzinfo=timezone.utc)
    last_watering_duration: timedelta = timedelta(seconds=900)

    async def setup(self):

        # fetch sqlite latest states (SSOT)

        try:
            latest_watering_events = await fetch_latest_watering_events(
                sqlite_db_name=self.sqlite_db_name,
                watering_events_table=self.sqlite_events_table,
            )
        except Exception as err:
            raise WateringEventFetchingFailed(
                f"Fetching watering events from DB failed due to {err}"
            )

        latest_event = sorted(latest_watering_events, key=lambda x: x[0], reverse=True)[
            0
        ]
        self.last_watering = datetime.fromisoformat(latest_event[0]).replace(
            tzinfo=timezone.utc
        )
        self.last_watering_duration = timedelta(seconds=latest_event[1])

    async def setup_watering_GPIO(self):

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

        # However, the GPIO pin for the pump relay needs to be set to HIGH
        # to ensure the pump is off initially
        GPIO.output(self.pin, True)

    async def run_watering(self, duration_seconds: float = None) -> None:

        watering_duration = (
            duration_seconds if duration_seconds else self.watering_time_seconds
        )

        GPIO.output(self.pin, False)
        await asyncio.sleep(delay=watering_duration)
        GPIO.output(self.pin, True)

        timestamp = datetime.now(tz=timezone.utc).replace(microsecond=0)
        self.last_watering = timestamp
        self.last_watering_duration = timedelta(seconds=watering_duration)

        try:
            async with aiosqlite.connect(database=self.sqlite_db_name) as db:
                _ = await write_watering_event_to_db(
                    sqlite_client=db,
                    watering_events_table=self.sqlite_events_table,
                    timestamp=timestamp,
                    duration_seconds=watering_duration,
                )
                await db.close()
        except Exception as err:
            raise EventRecordFailed(
                f"Storing watering event in DB failed for pump {self.identifier} due to {err}"
            )

    async def cleanup(self) -> None:
        GPIO.output(self.pin, True)
        GPIO.cleanup(self.pin)
