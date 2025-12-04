from fastapi import APIRouter
from src.services.api.models.data import DataRequestProperties

from src.services.api.handlers.data import get_measurements as get_handlers_measurements

router = APIRouter()


@router.post("/", tags=["measurements"])
async def get_measurements(req_properties: DataRequestProperties):

    values = await get_handlers_measurements(req_properties=req_properties)

    return values


@router.post("/{sensor_identifier}", tags=["measurements"])
async def get_measurements(
    sensor_identifier: str, req_properties: DataRequestProperties
):

    values = await get_handlers_measurements(
        req_properties=req_properties,
        sensor_identifier=sensor_identifier,
    )

    return values
