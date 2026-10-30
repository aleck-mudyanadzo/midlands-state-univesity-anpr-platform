import uuid
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    registration_number = Column(String, nullable=False)
    normalized_registration_number = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=True)
    make = Column(String, nullable=True)
    model = Column(String, nullable=True)
    colour = Column(String, nullable=True)
    owner_category = Column(String, nullable=True)
    owner_reference = Column(String, nullable=True)
    status = Column(String, nullable=False, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"))
    deleted_at = Column(DateTime(timezone=True), nullable=True)