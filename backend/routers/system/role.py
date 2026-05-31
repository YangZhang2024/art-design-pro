from fastapi import APIRouter
from typing import Optional
from database import get_session, Role

router = APIRouter(prefix="/api/role", tags=["role"])


@router.get("/list")
def get_role_list(
    roleName: Optional[str] = None,
    roleCode: Optional[str] = None,
    description: Optional[str] = None,
    enabled: Optional[bool] = None,
    startTime: Optional[str] = None,
    endTime: Optional[str] = None,
    current: int = 1,
    size: int = 20,
):
    db = get_session()
    query = db.query(Role)
    if roleName: query = query.filter(Role.roleName.like(f"%{roleName}%"))
    if roleCode: query = query.filter(Role.roleCode.like(f"%{roleCode}%"))
    if description: query = query.filter(Role.description.like(f"%{description}%"))
    if enabled is not None: query = query.filter(Role.enabled == enabled)
    if startTime: query = query.filter(Role.createTime >= startTime)
    if endTime: query = query.filter(Role.createTime <= endTime)
    total = query.count()
    rows = query.offset((current - 1) * size).limit(size).all()
    records = []
    for r in rows:
        records.append({
            "roleId": r.id,
            "roleName": r.roleName,
            "roleCode": r.roleCode,
            "description": r.description,
            "enabled": r.enabled,
            "createTime": r.createTime or "",
        })
    db.close()
    return {"code": 200, "msg": "success", "data": {
        "records": records, "current": current, "size": size, "total": total
    }}
