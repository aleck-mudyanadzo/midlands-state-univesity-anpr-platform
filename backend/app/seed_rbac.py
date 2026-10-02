from app.core.database import SessionLocal
from app.models.rbac import Role, Permission, RolePermission, University, Campus, UserCampusRole
from app.models.user import User

ROLE_NAMES = [
    "SECURITY_OFFICER",
    "SECURITY_SUPERVISOR",
    "SECURITY_ADMIN",
    "SYSTEM_ADMIN",
    "AUDITOR",
    "REPORT_VIEWER",
]

PERMISSION_CODES = [
    "vehicle.read",
    "vehicle.create",
    "vehicle.update",
    "vehicle.revoke",
    "flag.read",
    "flag.create",
    "flag.remove",
    "access.approve",
    "access.deny",
    "reports.export",
    "audit.read",
    "system.configure",
    "gate.command",
]

# Starter mapping: which roles get which permissions (will be refined later)
ROLE_PERMISSIONS = {
    "SECURITY_OFFICER": ["vehicle.read", "flag.read", "access.approve", "access.deny"],
    "SECURITY_SUPERVISOR": [
        "vehicle.read", "vehicle.create", "vehicle.update",
        "flag.read", "flag.create", "flag.remove",
        "access.approve", "access.deny", "reports.export",
    ],
    "SECURITY_ADMIN": PERMISSION_CODES,  # full access
    "SYSTEM_ADMIN": ["system.configure", "audit.read"],
    "AUDITOR": ["audit.read", "vehicle.read", "flag.read"],
    "REPORT_VIEWER": ["reports.export"],
}


def seed_rbac():
    db = SessionLocal()
    try:
        # Roles
        roles = {}
        for name in ROLE_NAMES:
            role = db.query(Role).filter(Role.name == name).first()
            if not role:
                role = Role(name=name)
                db.add(role)
                db.flush()
            roles[name] = role

        # Permissions
        permissions = {}
        for code in PERMISSION_CODES:
            perm = db.query(Permission).filter(Permission.code == code).first()
            if not perm:
                perm = Permission(code=code)
                db.add(perm)
                db.flush()
            permissions[code] = perm

        # Role -> Permission mapping
        for role_name, perm_codes in ROLE_PERMISSIONS.items():
            role = roles[role_name]
            for code in perm_codes:
                perm = permissions[code]
                exists = (
                    db.query(RolePermission)
                    .filter(RolePermission.role_id == role.id, RolePermission.permission_id == perm.id)
                    .first()
                )
                if not exists:
                    db.add(RolePermission(role_id=role.id, permission_id=perm.id))

        db.commit()
        print(f"Seeded {len(ROLE_NAMES)} roles and {len(PERMISSION_CODES)} permissions.")

        # University + Campus
        university = db.query(University).filter(University.name == "Midlands State University").first()
        if not university:
            university = University(name="Midlands State University")
            db.add(university)
            db.flush()

        campus = db.query(Campus).filter(Campus.code == "GWERU").first()
        if not campus:
            campus = Campus(university_id=university.id, name="Gweru Main Campus", code="GWERU")
            db.add(campus)
            db.flush()

        db.commit()
        print(f"Seeded university and campus: {campus.name}")

        # Assign demo_officer the SECURITY_OFFICER role at Gweru
        demo_user = db.query(User).filter(User.username == "demo_officer").first()
        if demo_user:
            existing_assignment = (
                db.query(UserCampusRole)
                .filter(UserCampusRole.user_id == demo_user.id, UserCampusRole.campus_id == campus.id)
                .first()
            )
            if not existing_assignment:
                assignment = UserCampusRole(
                    user_id=demo_user.id,
                    campus_id=campus.id,
                    gate_id=None,
                    role_id=roles["SECURITY_OFFICER"].id,
                )
                db.add(assignment)
                db.commit()
                print("Assigned demo_officer the SECURITY_OFFICER role at Gweru Main Campus.")
            else:
                print("demo_officer already has a role assignment at this campus.")
        else:
            print("demo_officer not found - skipping role assignment.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_rbac()