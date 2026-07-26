from typing import Optional

from fastapi import HTTPException

from src.models.components.actuators import WaterPump


async def run_watering(pump: WaterPump, watering_duration: float | None = None) -> None:

    # We need to ensure that the watering system runs once
    # and the GPIO pin is cleaned up since the (default) output=False
    # leads to a situation where the pump is still running after the request is completed.
    # Therefore, we fully run the watering system setup and cleanup the GPIO pin in this function.

    try:
        _ = await pump.setup_watering_GPIO()
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Watering system setup couldn't be executed due to {err}.",
        )

    try:
        _ = await pump.run_watering(duration_seconds=watering_duration)
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Watering run couldn't be executed due to {err}.",
        )

    try:
        _ = await pump.cleanup()
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"""
                Pump GPIO cleanup couldn't be executed due to {err}.
                Watering may still be in progress!
            """,
        )
