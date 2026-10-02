from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.rbac import UserCampusRole, RolePermission, Permission


def require_permission(permission_code: str):
    def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        # Find all role assignments this user has (any campus/gate)
        assignments = (
            db.query(UserCampusRole)
            .filter(UserCampusRole.user_id == current_user.id)
            .all()
        )

        if not assignments:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no assigned role",
            )

        role_ids = [a.role_id for a in assignments]

        has_permission = (
            db.query(RolePermission)
            .join(Permission, Permission.id == RolePermission.permission_id)
            .filter(RolePermission.role_id.in_(role_ids), Permission.code == permission_code)
            .first()
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission_code}",
            )

        return current_user

    return checker