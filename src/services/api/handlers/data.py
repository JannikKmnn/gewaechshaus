from fastapi import HTTPException

from datetime import timedelta
from typing import Optional

from src.services.api.models.data import (
    DataRequestProperties,
    SoilMoistureIntervalsRequestProperties,
)
from src.models.enums import DynamicDataAggregation, SensorType
from src.services.api.db.data import fetch_measurements


def pick_aggregation(timediff):

    mapping_dict = {
        agg.value: int(agg.name.split("_")[1]) for agg in DynamicDataAggregation
    }
    items = sorted(mapping_dict.items(), key=lambda x: x[1])

    for i, (key, value) in enumerate(items):
        # last item → return it
        if i == len(items) - 1:
            return key

        next_value = items[i + 1][1]

        if value <= timediff < next_value:
            return key


async def get_measurements(
    req_properties: DataRequestProperties, sensor_identifier: Optional[str] = None
) -> list[dict]:

    if req_properties.end_time and req_properties.end_time <= req_properties.start_time:
        raise HTTPException(
            status_code=400, detail="Query end time must be after start time."
        )

    timediff: timedelta = req_properties.end_time - req_properties.start_time
    timediff_days: int = timediff.days

    aggregation = None
    if timediff_days >= int(list(DynamicDataAggregation)[0].name.split("_")[1]):
        aggregation = pick_aggregation(timediff=timediff_days)

    values = await fetch_measurements(
        start_time=req_properties.start_time,
        measurement=req_properties.measurement,
        end_time=req_properties.end_time,
        field_identifier=[sensor_identifier] if sensor_identifier else None,
        aggregation=aggregation,
    )

    return [
        {
            "measurement": val[0],
            "field": val[1],
            "timestamp": val[2],
            "value": val[3],
        }
        for val in values
    ]


async def get_soil_moisture_intervals(
    req_properties: SoilMoistureIntervalsRequestProperties,
) -> list[dict]:

    if req_properties.end_time <= req_properties.start_time:
        raise HTTPException(
            status_code=400, detail="Query end time must be after start time."
        )

    soil_moisture_state_changes = await fetch_measurements(
        start_time=req_properties.start_time,
        measurement=SensorType.SOIL_MOISTURE,
        end_time=req_properties.end_time,
        field_identifier=[req_properties.sensor_identifier],
        binary_state_changes_identifier="wet",
    )

    soil_moisture_intervals = [
        {
            "from": req_properties.start_time.isoformat(),
            "to": (
                soil_moisture_state_changes[0][2]
                if len(soil_moisture_state_changes) > 0
                else req_properties.end_time.isoformat()
            ),
            "state": (
                "dry"
                if len(soil_moisture_state_changes) > 0
                and soil_moisture_state_changes[0][3] == "wet"
                else "wet"
            ),
        }
    ]

    if len(soil_moisture_state_changes) > 0:
        for i in range(len(soil_moisture_state_changes) - 1):
            soil_moisture_intervals.append(
                {
                    "from": soil_moisture_state_changes[i][2],
                    "to": soil_moisture_state_changes[i + 1][2],
                    "state": soil_moisture_state_changes[i][3],
                }
            )

        soil_moisture_intervals.append(
            {
                "from": soil_moisture_state_changes[-1][2],
                "to": req_properties.end_time.isoformat(),
                "state": soil_moisture_state_changes[-1][3],
            }
        )

    return soil_moisture_intervals
