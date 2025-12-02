import asyncio
import sys

from src.services.sensor_reader.setup import setup_linear_actuators

WINDOW_ACTUATOR_LEFT_EXTEND_PIN = 5
WINDOW_ACTUATOR_LEFT_RETRACT_PIN = 6

WINDOW_ACTUATOR_RIGHT_EXTEND_PIN = 16
WINDOW_ACTUATOR_RIGHT_RETRACT_PIN = 20

MOVE_TIME = 15.0


async def main(position, movement):

    left_actuator, right_actuator = setup_linear_actuators(
        left_extend_pin=WINDOW_ACTUATOR_LEFT_EXTEND_PIN,
        left_retract_pin=WINDOW_ACTUATOR_LEFT_RETRACT_PIN,
        right_extend_pin=WINDOW_ACTUATOR_RIGHT_EXTEND_PIN,
        right_retract_pin=WINDOW_ACTUATOR_RIGHT_RETRACT_PIN,
        moving_time=MOVE_TIME,
    )

    if not position and not movement:

        assert not left_actuator.is_extended
        assert not right_actuator.is_extended

        _ = await asyncio.gather(left_actuator.extend(), right_actuator.extend())

        await asyncio.sleep(5.0)

        assert left_actuator.is_extended
        assert right_actuator.is_extended

        _ = await asyncio.gather(left_actuator.retract(), right_actuator.retract())

        assert not left_actuator.is_extended
        assert not right_actuator.is_extended

    if position == "left":
        actuator_to_test = left_actuator
    elif position == "right":
        actuator_to_test = right_actuator

    if actuator_to_test:
        if movement == "extend":
            await actuator_to_test.extend()
            assert actuator_to_test.is_extended
        elif movement == "retract":
            await actuator_to_test.retract()
            assert not actuator_to_test.is_extended
        else:
            # opens and closes window if closed
            await actuator_to_test.extend()
            assert actuator_to_test.is_extended
            await asyncio.sleep(5.0)
            await actuator_to_test.retract()
            assert not actuator_to_test.is_extended

    await asyncio.sleep(5.0)

    return


if __name__ == "__main__":

    position = None
    movement = None

    if sys.argv[1]:
        position = sys.argv[1]

    if sys.argv[2]:
        movement = sys.argv[2]

    asyncio.run(main(position=position, movement=movement))
