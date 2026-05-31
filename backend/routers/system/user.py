from fastapi import APIRouter, Header, Depends, HTTPException
from typing import Optional
import json
from database import get_session, User, Role, UserRole

router = APIRouter(prefix="/api/user", tags=["user"])

JWT_SECRET = "art-design-dev-secret-key"
JWT_ALGO = "HS256"


@router.get("/list")
def get_user_list(
    userName: Optional[str] = None,
    userGender: Optional[str] = None,
    userPhone: Optional[str] = None,
    userEmail: Optional[str] = None,
    status: Optional[str] = None,
    current: int = 1,
    size: int = 20,
    authorization: str = Header(""),
):
    db = get_session()
    query = db.query(User)
    if userName: query = query.filter(User.userName.ilike(f"%{userName}%"))
    if userGender: query = query.filter(User.userGender == userGender)
    if userPhone: query = query.filter(User.userPhone.like(f"%{userPhone}%"))
    if userEmail: query = query.filter(User.userEmail.ilike(f"%{userEmail}%"))
    if status: query = query.filter(User.status == status)
    total = query.count()
    rows = query.offset((current - 1) * size).limit(size).all()
    records = []
    for u in rows:
        records.append({
            "id": u.id,
            "avatar": u.avatar or "",
            "status": u.status,
            "userName": u.userName,
            "userGender": u.userGender,
            "nickName": u.nickName,
            "userPhone": u.userPhone,
            "userEmail": u.userEmail,
            "userRoles": [r.roleCode for r in u.roles],
            "createBy": "admin",
            "createTime": u.createTime or "",
            "updateBy": "admin",
            "updateTime": u.updateTime or "",
        })
    db.close()
    return {"code": 200, "msg": "success", "data": {
        "records": records, "current": current, "size": size, "total": total
    }}
