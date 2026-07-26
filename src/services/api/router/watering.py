import asyncio

from fastapi import APIRouter, Request, HTTPException
from src.services.api.models.watering import WateringRequestProperties
import os

try:
    from src.services.api.handlers import watering
except ModuleNotFoundError:
    # happens on local dev
    pass

router = APIRouter()


@router.post("/run_watering", tags=["pump"])
async def run_watering(watering_request: WateringRequestProperties, request: Request):

    watering_pump = request.app.state.watering_system

    _ = await watering.run_watering(
        pump=watering_pump, watering_duration=watering_request.watering_time_seconds
    )
