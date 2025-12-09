import asyncio
import sys

from dotenv import load_dotenv

load_dotenv()

from src.shared.actuators import setup_window_openers

WINDOW_ACTUATOR_LEFT_EXTEND_PIN = 5
WINDOW_ACTUATOR_LEFT_RETRACT_PIN = 6

WINDOW_ACTUATOR_RIGHT_EXTEND_PIN = 16
WINDOW_ACTUATOR_RIGHT_RETRACT_PIN = 20

MOVE_TIME = 15.0


async def main(position, movement):

    window_actuators = await setup_window_openers()
    assert len(window_actuators) == 2
    left_actuator = window_actuators[0]
    right_actuator = window_actuators[1]

    actuator_to_test = None

    if position == "left":
        actuator_to_test = left_actuator
    elif position == "right":
        actuator_to_test = right_actuator

    if actuator_to_test:
        if movement == "extend":
            actuator_to_test.is_extended = False
            await actuator_to_test.extend()
            assert actuator_to_test.is_extended
        elif movement == "retract":
            actuator_to_test.is_extended = True
            await actuator_to_test.retract()
            assert not actuator_to_test.is_extended
        else:
            await actuator_to_test.extend()
            assert actuator_to_test.is_extended
            await asyncio.sleep(5.0)
            await actuator_to_test.retract()
            assert not actuator_to_test.is_extended
    else:
        # opens and closes window if closed
        print("Opening Windows..")
        _ = await asyncio.gather(left_actuator.extend(), right_actuator.extend())
        assert left_actuator.is_extended
        assert right_actuator.is_extended
        print("Windows open.")
        await asyncio.sleep(5.0)
        print("Closing Windows..")
        _ = await asyncio.gather(left_actuator.retract(), right_actuator.retract())
        assert not left_actuator.is_extended
        assert not right_actuator.is_extended
        print("Windows closed.")

    await asyncio.sleep(5.0)

    return


if __name__ == "__main__":

    position = None
    movement = None

    try:
        position = sys.argv[1]
    except IndexError:
        print("Running both positions..")

    try:
        movement = sys.argv[2]
    except IndexError:
        print("Open and close..")

    asyncio.run(main(position=position, movement=movement))

    print("Test done.")
