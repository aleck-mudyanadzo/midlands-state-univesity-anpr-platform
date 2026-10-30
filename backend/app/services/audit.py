from sqlalchemy.orm import Session
from app.models.audit import AuditLog


def write_audit_log(
    db: Session,
    actor_id,
    action: str,
    resource_type: str,
    resource_id=None,
    result: str = "SUCCESS",
    metadata: dict | None = None,
    ip_address: str | None = None,
    request_id: str | None = None,
):
    entry = AuditLog(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        result=result,
        metadata_json=metadata,
        ip_address=ip_address,
        request_id=request_id,
    )
    db.add(entry)
    db.commit()
    return entry