from fastapi import HTTPException

from src.models.components.actuators import LinearActuator
from src.models.exceptions import StateAlreadyReached, EventRecordFailed
from src.services.api.models.data import WindowEventsRequestProperties
from src.services.api.db.windows import (
    get_window_events as get_db_window_events,
    get_window_configurations as get_db_window_configurations,
)


async def open_window(actuator: LinearActuator):
    try:
        _ = await actuator.extend()
    except StateAlreadyReached:
        raise HTTPException(
            status_code=409,
            detail=f"{actuator.position.value} actuator is already opened.",
        )
    except EventRecordFailed as err:
        raise HTTPException(
            status_code=500,
            detail=f"Storing event into sqlite DB failed for window {actuator.position.value} due to {err}",
        )


async def close_window(actuator: LinearActuator):
    try:
        _ = await actuator.retract()
    except StateAlreadyReached:
        raise HTTPException(
            status_code=409,
            detail=f"{actuator.position.value} actuator is already closed.",
        )
    except EventRecordFailed as err:
        raise HTTPException(
            status_code=500,
            detail=f"Storing event into sqlite DB failed for window {actuator.position.value} due to {err}",
        )


async def get_window_status(actuator: LinearActuator):

    return_dict = {
        "last_opening": actuator.last_extension,
        "last_closing": actuator.last_retraction,
    }

    if actuator.is_extended:
        return_dict["status"] = "open"
    else:
        return_dict["status"] = "closed"

    return return_dict


async def get_window_events(
    actuator_events_table: str, req_properties: WindowEventsRequestProperties
):

    if (req_properties.end_time and req_properties.start_time) and (
        req_properties.end_time <= req_properties.start_time
    ):
        raise HTTPException(
            status_code=400, detail="Query end time must be after start time."
        )

    results = await get_db_window_events(
        actuator_events_table=actuator_events_table,
        identifier=req_properties.window_identifier,
        start_time=req_properties.start_time,
        end_time=req_properties.end_time,
    )

    return results


async def get_window_configurations(window_entity_table: str, window_identifier: str):
    result = await get_db_window_configurations(
        identifier=window_identifier,
        window_entity_table=window_entity_table,
    )

    return result
