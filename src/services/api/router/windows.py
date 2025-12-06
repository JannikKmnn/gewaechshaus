from fastapi import APIRouter, Request, HTTPException

from src.services.api.handlers import windows

router = APIRouter()


@router.post("/open/{window_position}", tags=["actuators"])
async def open_window(window_position: str, request: Request):
    window_openers = request.app.state.actuators

    requested_position = window_position.lower()

    try:
        window_to_open = next(
            win
            for win in window_openers
            if win.position.value.lower() == requested_position
        )
    except StopIteration:
        raise HTTPException(
            status_code=400,
            detail=f"Window on position {window_position} not initialized.",
        )

    _ = await windows.open_window(actuator=window_to_open)


@router.post("/close/{window_position}", tags=["actuators"])
async def close_window(window_position: str, request: Request):
    window_openers = request.app.state.actuators

    requested_position = window_position.lower()

    try:
        window_to_close = next(
            win
            for win in window_openers
            if win.position.value.lower() == requested_position
        )
    except StopIteration:
        raise HTTPException(
            status_code=400,
            detail=f"Window on position {window_position} not initialized.",
        )

    _ = await windows.close_window(actuator=window_to_close)
