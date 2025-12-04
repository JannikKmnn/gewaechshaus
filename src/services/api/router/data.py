from fastapi import APIRouter
from models.data import DataRequestProperties

from handlers.data import get_measurements as get_handlers_measurements

router = APIRouter()


@router.get("/", tags=["measurements"])
async def get_measurements(req_properties: DataRequestProperties):

    values = await get_handlers_measurements(
        req_properties=req_properties
    )

    return values


@router.get("/{sensor_identifier}", tags=["measurements"])
async def get_measurements(
    sensor_identifier: str, req_properties: DataRequestProperties
):
    
    values = await get_handlers_measurements(
        req_properties=req_properties,
        sensor_identifier=sensor_identifier,
    )
    
    return values
