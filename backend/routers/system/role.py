from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/api/role", tags=["role"])

roles = [
    {"roleId": 1, "roleName": "超级管理员", "roleCode": "R_SUPER", "description": "拥有系统全部权限", "enabled": True, "createTime": "2025-05-15 12:30:45"},
    {"roleId": 2, "roleName": "管理员", "roleCode": "R_ADMIN", "description": "拥有系统管理权限", "enabled": True, "createTime": "2025-05-15 12:30:45"},
    {"roleId": 3, "roleName": "普通用户", "roleCode": "R_USER", "description": "拥有系统普通权限", "enabled": True, "createTime": "2025-05-15 12:30:45"},
    {"roleId": 4, "roleName": "财务管理员", "roleCode": "R_FINANCE", "description": "管理财务相关权限", "enabled": True, "createTime": "2025-05-16 09:15:30"},
    {"roleId": 5, "roleName": "数据分析师", "roleCode": "R_ANALYST", "description": "拥有数据分析权限", "enabled": False, "createTime": "2025-05-16 11:45:00"},
    {"roleId": 6, "roleName": "客服专员", "roleCode": "R_SUPPORT", "description": "处理客户支持请求", "enabled": True, "createTime": "2025-05-17 14:30:22"},
    {"roleId": 7, "roleName": "营销经理", "roleCode": "R_MARKETING", "description": "管理营销活动权限", "enabled": True, "createTime": "2025-05-17 15:10:50"},
    {"roleId": 8, "roleName": "访客用户", "roleCode": "R_GUEST", "description": "仅限浏览权限", "enabled": False, "createTime": "2025-05-18 08:25:40"},
]

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
    result = list(roles)
    if roleName: result = [r for r in result if roleName in r["roleName"]]
    if roleCode: result = [r for r in result if roleCode in r["roleCode"]]
    if description: result = [r for r in result if description in r["description"]]
    if enabled is not None: result = [r for r in result if r["enabled"] == enabled]
    if startTime: result = [r for r in result if r["createTime"][:10] >= startTime]
    if endTime: result = [r for r in result if r["createTime"][:10] <= endTime]
    total = len(result)
    start = (current - 1) * size
    return {"code": 200, "msg": "success", "data": {
        "records": result[start:start + size],
        "current": current, "size": size, "total": total,
    }}
