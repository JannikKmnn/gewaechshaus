import os

from src.models.components.actuators import LinearActuator
from src.models.enums import Position


def setup_linear_actuators(
    left_extend_pin: int,
    left_retract_pin: int,
    right_extend_pin: int,
    right_retract_pin: int,
    moving_time: float,
) -> list[LinearActuator]:

    actuator_left = LinearActuator(
        identifier="linear_actuator_left",
        position=Position.LEFT,
        extend_pin=left_extend_pin,
        retract_pin=left_retract_pin,
        moving_time_seconds=moving_time,
    )

    actuator_left.setup()

    actuator_right = LinearActuator(
        identifier="linear_actuator_right",
        position=Position.RIGHT,
        extend_pin=right_extend_pin,
        retract_pin=right_retract_pin,
        moving_time_seconds=moving_time,
    )

    actuator_right.setup()

    return [actuator_left, actuator_right]


async def setup_window_openers() -> list[LinearActuator]:

    window_actuators = setup_linear_actuators(
        left_extend_pin=int(os.getenv("WINDOW_ACTUATOR_LEFT_EXTEND_PIN")),
        left_retract_pin=int(os.getenv("WINDOW_ACTUATOR_LEFT_RETRACT_PIN")),
        right_extend_pin=int(os.getenv("WINDOW_ACTUATOR_RIGHT_EXTEND_PIN")),
        right_retract_pin=int(os.getenv("WINDOW_ACTUATOR_RIGHT_RETRACT_PIN")),
        moving_time=float(os.getenv("WINDOW_MOVING_TIME")),
    )

    return window_actuators
