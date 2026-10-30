import re
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import require_permission
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from app.services.audit import write_audit_log

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


def normalize_plate(raw: str) -> str:
    # Basic normalization: uppercase, strip extra whitespace.
    # Full configurable format validation comes later (per SRS FR-009).
    return re.sub(r"\s+", " ", raw.strip().upper())


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    payload: VehicleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("vehicle.create")),
):
    normalized = normalize_plate(payload.registration_number)

    existing = db.query(Vehicle).filter(Vehicle.normalized_registration_number == normalized).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vehicle with this plate already exists")

    vehicle = Vehicle(
        registration_number=payload.registration_number,
        normalized_registration_number=normalized,
        vehicle_type=payload.vehicle_type,
        make=payload.make,
        model=payload.model,
        colour=payload.colour,
        owner_category=payload.owner_category,
        owner_reference=payload.owner_reference,
        status="ACTIVE",
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    write_audit_log(
        db,
        actor_id=current_user.id,
        action="VEHICLE_CREATED",
        resource_type="vehicle",
        resource_id=vehicle.id,
        result="SUCCESS",
        metadata={"registration_number": normalized},
        ip_address=request.client.host if request.client else None,
    )

    return vehicle


@router.get("", response_model=list[VehicleResponse])
def list_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("vehicle.read")),
    limit: int = 50,
    offset: int = 0,
):
    vehicles = (
        db.query(Vehicle)
        .filter(Vehicle.deleted_at.is_(None))
        .order_by(Vehicle.created_at.desc())
        .offset(offset)
        .limit(min(limit, 200))
        .all()
    )
    return vehicles


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("vehicle.read")),
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.deleted_at.is_(None)).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return vehicle


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: uuid.UUID,
    payload: VehicleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("vehicle.update")),
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.deleted_at.is_(None)).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)

    db.commit()
    db.refresh(vehicle)

    write_audit_log(
        db,
        actor_id=current_user.id,
        action="VEHICLE_UPDATED",
        resource_type="vehicle",
        resource_id=vehicle.id,
        result="SUCCESS",
        metadata={"updated_fields": list(update_data.keys())},
        ip_address=request.client.host if request.client else None,
    )

    return vehicle