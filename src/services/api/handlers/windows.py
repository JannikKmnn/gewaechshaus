from fastapi import HTTPException

from src.models.components.actuators import LinearActuator
from src.models.exceptions import StateAlreadyReached, EventRecordFailed
from src.models.enums import WindowCombination
from src.services.api.models.windows import (
    WindowEventsRequestProperties,
    WindowIntervalsRequestProperties,
    WindowConfigurationResponseProperties,
    WindowConfigurationUpdateProperties,
)
from src.services.api.db.windows import (
    get_window_events as get_db_window_events,
    get_window_configurations as get_db_window_configurations,
    update_window_configurations as update_db_window_configurations,
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


async def get_window_intervals(
    actuator_events_table: str, req_properties: WindowIntervalsRequestProperties
):

    if (req_properties.end_time and req_properties.start_time) and (
        req_properties.end_time <= req_properties.start_time
    ):
        raise HTTPException(
            status_code=400, detail="Query end time must be after start time."
        )

    events = await get_db_window_events(
        actuator_events_table=actuator_events_table,
        start_time=req_properties.start_time,
        end_time=req_properties.end_time,
    )

    if len(events) == 0:
        return [
            {
                "from": req_properties.start_time.isoformat(),
                "to": req_properties.end_time.isoformat(),
                "state": WindowCombination.UNKNOWN,
            }
        ]

    first_left_position = next(
        (res for res in events if res[0] == "linear_actuator_left"), None
    )
    first_right_position = next(
        (res for res in events if res[0] == "linear_actuator_right"), None
    )

    if first_left_position is not None:
        left = first_left_position[2] == 0
    else:
        left = (
            first_right_position[2] == 1 if first_right_position is not None else False
        )

    if first_right_position is not None:
        right = first_right_position[2] == 0
    else:
        right = (
            first_left_position[2] == 1 if first_left_position is not None else False
        )

    last_timestamp = req_properties.start_time.isoformat()
    intervals = []

    for identifier, timestamp, status in events:

        intervals.append(
            {
                "from": last_timestamp,
                "to": timestamp,
                "state": (
                    WindowCombination.BOTH
                    if left and right
                    else (
                        WindowCombination.LEFT
                        if left
                        else (
                            WindowCombination.RIGHT
                            if right
                            else WindowCombination.CLOSED
                        )
                    )
                ),
            }
        )

        if identifier == "linear_actuator_left":
            left = bool(status)
        elif identifier == "linear_actuator_right":
            right = bool(status)

        last_timestamp = timestamp

    intervals.append(
        {
            "from": last_timestamp,
            "to": req_properties.end_time.isoformat(),
            "state": (
                WindowCombination.BOTH
                if left and right
                else (
                    WindowCombination.LEFT
                    if left
                    else WindowCombination.RIGHT if right else WindowCombination.CLOSED
                )
            ),
        }
    )

    return intervals


async def get_window_configurations(window_entity_table: str, window_identifier: str):
    result = await get_db_window_configurations(
        identifier=window_identifier,
        window_entity_table=window_entity_table,
    )

    return WindowConfigurationResponseProperties(
        window_identifier=result[0], inside_temperature_opening_threshold=result[1]
    )


async def update_window_configurations(
    window_entity_table: str,
    window_identifier: str,
    update_properties: WindowConfigurationUpdateProperties,
):
    try:
        _ = await update_db_window_configurations(
            identifier=window_identifier,
            window_entity_table=window_entity_table,
            updates=update_properties,
        )
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Updating config of {window_identifier} failed due to: {err}",
        )

    return update_properties.dict()
