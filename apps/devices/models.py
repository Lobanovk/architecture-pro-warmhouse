from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class DeviceStatus(str, Enum):
    PENDING_CONNECTION = "pending_connection"
    ACTIVE = "active"
    INACTIVE = "inactive"


class CommandStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DONE = "done"
    FAILED = "failed"


class DeviceCreate(BaseModel):
    name: str = Field(max_length=100)
    type_id: int
    serial_number: str = Field(max_length=100)
    room_id: int | None = None


class DeviceRoomUpdate(BaseModel):
    room_id: int | None


class Device(BaseModel):
    id: int
    house_id: int
    room_id: int | None = None
    type_id: int
    serial_number: str
    name: str
    value: float | None = None
    status: DeviceStatus
    last_updated: datetime | None = None
    created_at: datetime


class CommandCreate(BaseModel):
    name: str
    params: dict[str, Any] = {}


class Command(BaseModel):
    id: UUID
    device_id: int
    name: str
    params: dict[str, Any] = {}
    status: CommandStatus
    created_at: datetime
