import uuid
from datetime import datetime
from pydantic import BaseModel


class VehicleCreate(BaseModel):
    registration_number: str
    vehicle_type: str | None = None
    make: str | None = None
    model: str | None = None
    colour: str | None = None
    owner_category: str | None = None
    owner_reference: str | None = None


class VehicleUpdate(BaseModel):
    vehicle_type: str | None = None
    make: str | None = None
    model: str | None = None
    colour: str | None = None
    owner_category: str | None = None
    owner_reference: str | None = None
    status: str | None = None


class VehicleResponse(BaseModel):
    id: uuid.UUID
    registration_number: str
    normalized_registration_number: str
    vehicle_type: str | None
    make: str | None
    model: str | None
    colour: str | None
    owner_category: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True