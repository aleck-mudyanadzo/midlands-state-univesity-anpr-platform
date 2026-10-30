import uuid
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    timestamp = Column("timestamp", DateTime(timezone=True), server_default=text("now()"))
    actor_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(String, nullable=True)
    result = Column(String, nullable=False)
    metadata_json = Column("metadata", JSONB, nullable=True)
    request_id = Column(String, nullable=True)