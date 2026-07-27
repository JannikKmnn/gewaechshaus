from fastapi import APIRouter, Request
from src.services.api.models.watering import (
    WateringRequestProperties,
    WateringEventsRequestProperties,
)

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


@router.post("/events", tags=["pump"])
async def get_window_events(
    req_properties: WateringEventsRequestProperties, request: Request
):

    watering_pump = request.app.state.watering_system

    results = await watering.get_watering_events(
        watering_events_table=watering_pump.sqlite_events_table,
        req_properties=req_properties,
    )

    return results


@router.get("/events/latest", tags=["pump"])
async def get_latest_watering_event(request: Request):

    watering_pump = request.app.state.watering_system

    return await watering.get_latest_watering_event(pump=watering_pump)
