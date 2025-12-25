import asyncio

from fastapi import APIRouter, Request, HTTPException

try:
    from src.services.api.handlers import windows
except ModuleNotFoundError:
    pass

router = APIRouter()


@router.post("/open", tags=["actuators"])
async def open_windows(request: Request):
    window_openers = request.app.state.actuators

    _ = await asyncio.gather(
        *[windows.open_window(actuator=act) for act in window_openers],
        return_exceptions=True,
    )


@router.post("/close", tags=["actuators"])
async def close_windows(request: Request):
    window_openers = request.app.state.actuators

    _ = await asyncio.gather(
        *[windows.close_window(actuator=act) for act in window_openers],
        return_exceptions=True,
    )


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


@router.get("/status/{window_position}", tags=["actuators"])
async def get_window_status(window_position: str, request: Request):
    window_actuators = request.app.state.actuators

    requested_position = window_position.lower()

    try:
        window_to_close = next(
            win
            for win in window_actuators
            if win.position.value.lower() == requested_position
        )
    except StopIteration:
        raise HTTPException(
            status_code=400,
            detail=f"Window on position {window_position} not initialized.",
        )

    return await windows.get_window_status(actuator=window_to_close)
