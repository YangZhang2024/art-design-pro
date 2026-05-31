from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/api/user", tags=["user"])

# --- in-memory data matching frontend UserListItem ---
users = [
    {"id": 1, "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=alex", "status": "1", "userName": "Alex Morgan", "userGender": "男", "nickName": "Alex", "userPhone": "18670001591", "userEmail": "alexmorgan@company.com", "userRoles": ["R_SUPER"], "createBy": "admin", "createTime": "2020-09-09 10:01:10", "updateBy": "admin", "updateTime": "2026-05-28 14:00:00"},
    {"id": 2, "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=sophia", "status": "1", "userName": "Sophia Baker", "userGender": "女", "nickName": "Sophia", "userPhone": "17766664444", "userEmail": "sophiabaker@company.com", "userRoles": ["R_ADMIN"], "createBy": "admin", "createTime": "2020-10-10 13:01:12", "updateBy": "admin", "updateTime": "2026-05-27 16:20:00"},
    {"id": 3, "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=liam", "status": "2", "userName": "Liam Park", "userGender": "男", "nickName": "Liam", "userPhone": "18670001597", "userEmail": "liampark@company.com", "userRoles": ["R_USER"], "createBy": "admin", "createTime": "2020-11-14 12:01:45", "updateBy": "admin", "updateTime": "2026-05-26 09:00:00"},
    {"id": 4, "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=olivia", "status": "1", "userName": "Olivia Grant", "userGender": "女", "nickName": "Olivia", "userPhone": "18670001596", "userEmail": "oliviagrant@company.com", "userRoles": ["R_ADMIN", "R_FINANCE"], "createBy": "admin", "createTime": "2020-11-14 09:01:20", "updateBy": "admin", "updateTime": "2026-05-25 11:30:00"},
    {"id": 5, "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=emma", "status": "3", "userName": "Emma Wilson", "userGender": "女", "nickName": "Emma", "userPhone": "18670001595", "userEmail": "emmawilson@company.com", "userRoles": ["R_USER"], "createBy": "admin", "createTime": "2020-11-13 11:01:05", "updateBy": "admin", "updateTime": "2026-05-24 08:45:00"},
    {"id": 6, "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=noah", "status": "1", "userName": "Noah Evan", "userGender": "男", "nickName": "Noah", "userPhone": "18670001594", "userEmail": "noahevan@company.com", "userRoles": ["R_MARKETING"], "createBy": "admin", "createTime": "2020-10-11 13:10:26", "updateBy": "admin", "updateTime": "2026-05-29 10:00:00"},
    {"id": 7, "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=ava", "status": "4", "userName": "Ava Martin", "userGender": "女", "nickName": "Ava", "userPhone": "18123820191", "userEmail": "avamartin@company.com", "userRoles": ["R_SUPPORT"], "createBy": "admin", "createTime": "2020-05-14 12:05:10", "updateBy": "admin", "updateTime": "2026-05-18 12:00:00"},
]

@router.get("/list")
def get_user_list(
    userName: Optional[str] = None,
    userGender: Optional[str] = None,
    userPhone: Optional[str] = None,
    userEmail: Optional[str] = None,
    status: Optional[str] = None,
    current: int = 1,
    size: int = 20,
):
    result = list(users)
    if userName: result = [u for u in result if userName.lower() in u["userName"].lower()]
    if userGender: result = [u for u in result if u["userGender"] == userGender]
    if userPhone: result = [u for u in result if userPhone in u["userPhone"]]
    if userEmail: result = [u for u in result if userEmail.lower() in u["userEmail"].lower()]
    if status: result = [u for u in result if u["status"] == status]
    total = len(result)
    start = (current - 1) * size
    return {"code": 200, "msg": "success", "data": {
        "records": result[start:start + size],
        "current": current, "size": size, "total": total,
    }}

@router.get("/info")
def get_user_info():
    return {"code": 200, "msg": "success", "data": {
        "buttons": ["add", "edit", "delete"],
        "roles": ["R_SUPER"],
        "userId": 1,
        "userName": "Admin",
        "email": "admin@company.com",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=admin",
    }}
