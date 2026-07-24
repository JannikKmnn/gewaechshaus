from fastapi import HTTPException

from src.models.components.actuators import WaterPump

async def run_watering(pump: WaterPump):

    try:
        _ = await pump.run_watering()
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Watering run couldn't be executed due to {err}.",
        )