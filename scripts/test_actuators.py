import asyncio
import sys

from src.services.sensor_reader.setup import setup_linear_actuators

import RPi.GPIO as GPIO  # type: ignore


async def main(position, movement):

    window_actuator_left_extend_pin = 5
    window_actuator_left_retract_pin = 6

    window_actuator_right_extend_pin = 16
    window_actuator_right_retract_pin = 20

    move_time = 15.0

    left_actuator, right_actuator = setup_linear_actuators(
        left_extend_pin=window_actuator_left_extend_pin,
        left_retract_pin=window_actuator_left_retract_pin,
        right_extend_pin=window_actuator_right_extend_pin,
        right_retract_pin=window_actuator_right_retract_pin,
        moving_time=move_time,
    )

    if not position and not movement:
        _ = await asyncio.gather(left_actuator.extend, right_actuator.extend)

        await asyncio.sleep(5.0)

        _ = await asyncio.gather(left_actuator.retract, right_actuator.retract)

    await asyncio.sleep(5.0)

    GPIO.cleanup()

    return


if __name__ == "__main__":

    position = None
    movement = None

    if sys.argv[1]:
        position = sys.argv[1]

    if sys.argv[2]:
        movement = sys.argv[2]

    asyncio.run(main(position=position, movement=movement))
