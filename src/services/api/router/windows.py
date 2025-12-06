from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/open/{window_position}", tags=["actuators"])
async def open_window(request: Request):
    pass


@router.post("/close/{window_position}", tags=["actuators"])
async def close_window(request: Request):
    pass
