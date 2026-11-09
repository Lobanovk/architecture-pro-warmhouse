import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from psycopg.errors import UniqueViolation

from broker import CommandPublisher
from models import Command, CommandCreate, Device, DeviceCreate, DeviceRoomUpdate, CommandStatus
from repository import DeviceRepository

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/devices")
MQTT_URL = os.getenv("MQTT_URL", "mqtt://localhost:1883")


@asynccontextmanager
async def lifespan(app: FastAPI):
    repo = DeviceRepository(DATABASE_URL)
    repo.init_schema()
    publisher = CommandPublisher(MQTT_URL)
    app.state.repo = repo
    app.state.publisher = publisher
    yield
    publisher.close()
    repo.close()


app = FastAPI(title="devices", lifespan=lifespan)


def get_repo(request: Request) -> DeviceRepository:
    return request.app.state.repo


def get_publisher(request: Request) -> CommandPublisher:
    return request.app.state.publisher


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v2/houses/{house_id}/devices", response_model=Device, status_code=status.HTTP_201_CREATED)
def create_device(house_id: int, data: DeviceCreate, repo: DeviceRepository = Depends(get_repo)):
    try:
        return repo.create(house_id, data)
    except UniqueViolation:
        raise HTTPException(status.HTTP_409_CONFLICT, "Device with serial_number {data.serial_number} already exists")


@app.get("/api/v2/devices/{device_id}", response_model=Device)
def get_device(device_id: int, repo: DeviceRepository = Depends(get_repo)):
    device = repo.get(device_id)
    if device is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Device not found")

    return device


@app.patch("/api/v2/devices/{device_id}", response_model=Device)
def update_device_room(device_id: int, data: DeviceRoomUpdate, repo: DeviceRepository = Depends(get_repo)):
    device = repo.update_room(device_id, data.room_id)
    if device is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Device not found")

    return device


@app.delete("/api/v2/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: int, repo: DeviceRepository = Depends(get_repo)):
    if not repo.delete(device_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Device not found")


@app.post("/api/v2/devices/{device_id}/commands", response_model=Command, status_code=status.HTTP_202_ACCEPTED)
def send_command(
    device_id: int,
    data: CommandCreate,
    repo: DeviceRepository = Depends(get_repo),
    publisher: CommandPublisher = Depends(get_publisher),
):
    if repo.get(device_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Device not found")

    command = Command(
        id = uuid4(),
        created_at = datetime.now(timezone.utc),
        device_id = device_id,
        status = CommandStatus.PENDING,
        name = data.name,
        params = data.params,
    )

    result = publisher.publish(command)

    command.status = CommandStatus.SENT if result else CommandStatus.FAILED

    return command
