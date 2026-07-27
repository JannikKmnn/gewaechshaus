from fastapi import HTTPException

from src.models.components.actuators import WaterPump
from src.services.api.db.watering import (
    get_watering_events as get_db_watering_events,
)
from src.services.api.models.windows import WindowEventsRequestProperties


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


async def get_watering_events(
    watering_events_table: str, req_properties: WindowEventsRequestProperties
):

    if (req_properties.end_time and req_properties.start_time) and (
        req_properties.end_time <= req_properties.start_time
    ):
        raise HTTPException(
            status_code=400, detail="Query end time must be after start time."
        )

    results = await get_db_watering_events(
        watering_events_table=watering_events_table,
        start_time=req_properties.start_time,
        end_time=req_properties.end_time,
    )

    return results


async def get_latest_watering_event(pump: WaterPump):

    return_dict = {
        "last_watering": pump.last_watering,
        "last_watering_duration": pump.last_watering_duration,
    }

    return return_dict
