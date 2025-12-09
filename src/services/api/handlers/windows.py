from fastapi import HTTPException

from src.models.components.actuators import LinearActuator
from src.models.exceptions import StateAlreadyReached


async def open_window(actuator: LinearActuator):
    try:
        _ = await actuator.extend()
    except StateAlreadyReached:
        raise HTTPException(
            status_code=409,
            detail=f"{actuator.position.value} actuator is already opened.",
        )


async def close_window(actuator: LinearActuator):
    try:
        _ = await actuator.retract()
    except StateAlreadyReached:
        raise HTTPException(
            status_code=409,
            detail=f"{actuator.position.value} actuator is already closed.",
        )
