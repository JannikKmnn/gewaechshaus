from fastapi import APIRouter
from src.services.api.models.data import (
    DataRequestProperties,
    SoilMoistureIntervalsRequestProperties,
)

from src.services.api.handlers.data import (
    get_measurements as get_handlers_measurements,
    get_soil_moisture_intervals as get_handlers_soil_moisture_intervals,
)

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


@router.post("/soil_moisture_intervals/{sensor_identifier}", tags=["measurements"])
async def get_soil_moisture_intervals(
    sensor_identifier: str, req_properties: SoilMoistureIntervalsRequestProperties
):

    results = await get_handlers_soil_moisture_intervals(
        req_properties=req_properties,
        sensor_identifier=sensor_identifier,
    )

    return results
