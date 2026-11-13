import random
from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="temperature-api")


class TemperatureResponse(BaseModel):
    value: float
    unit: str
    timestamp: datetime
    location: str
    status: str
    sensor_id: str
    sensor_type: str
    description: str


LOCATION_BY_SENSOR_ID = {
    "1": "Living Room",
    "2": "Bedroom",
    "3": "Kitchen",
}
SENSOR_ID_BY_LOCATION = {loc: id for id, loc in LOCATION_BY_SENSOR_ID.items()}

UNKNOWN_LOCATION = "Unknown"
UNKNOWN_SENSOR_ID = "0"


def build_response(location: str, sensor_id: str) -> TemperatureResponse:
    return TemperatureResponse(
        value=round(random.uniform(18.0, 26.0), 1),
        unit="°C",
        timestamp=datetime.now(timezone.utc),
        location=location,
        status="active",
        sensor_id=sensor_id,
        sensor_type="temperature",
        description=f"Temperature sensor in {location}",
    )


@app.get("/temperature", response_model=TemperatureResponse)
def get_by_location(location: str = "", sensor_id: str = ""):
    if not location:
        location = LOCATION_BY_SENSOR_ID.get(sensor_id, UNKNOWN_LOCATION)
    if not sensor_id:
        sensor_id = SENSOR_ID_BY_LOCATION.get(location, UNKNOWN_SENSOR_ID)
    return build_response(location, sensor_id)


@app.get("/temperature/{sensor_id}", response_model=TemperatureResponse)
def get_by_sensor_id(sensor_id: str):
    location = LOCATION_BY_SENSOR_ID.get(sensor_id, UNKNOWN_LOCATION)
    return build_response(location, sensor_id)
