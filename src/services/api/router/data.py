from fastapi import APIRouter
from models.data import DataRequestProperties

router = APIRouter()


@router.get("/", tags=["measurements"])
async def get_measurements(req_properties: DataRequestProperties):
    return


@router.get("/{sensor_identifier}", tags=["measurements"])
async def get_measurements(
    sensor_identifier: str, req_properties: DataRequestProperties
):
    return
