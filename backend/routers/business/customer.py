from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import copy

router = APIRouter(prefix="/api/customer", tags=["customer"])

# --- in-memory data ---
customers = [
    {"id": 10001, "name": "星河科技（上海）有限公司", "contactName": "张伟", "phone": "13800000001", "email": "zhangwei@startech.cn", "status": "1", "address": "上海市浦东新区张江高科技园区", "remark": "核心客户，季度采购量大", "createdAt": "2026-05-01 09:00:00", "updatedAt": "2026-05-28 14:30:00"},
    {"id": 10002, "name": "云帆贸易（深圳）有限公司", "contactName": "李娜", "phone": "13800000002", "email": "lina@yunfan.com", "status": "1", "address": "深圳市南山区科技园南区", "remark": "长期合作客户", "createdAt": "2026-05-04 10:15:00", "updatedAt": "2026-05-27 16:20:00"},
    {"id": 10003, "name": "青岚设计工作室", "contactName": "王强", "phone": "13800000003", "email": "wangqiang@qinglan.com", "status": "2", "address": "杭州市西湖区转塘街道", "remark": "已暂停合作", "createdAt": "2026-05-09 08:30:00", "updatedAt": "2026-05-20 11:00:00"},
    {"id": 10004, "name": "海盐智能制造有限公司", "contactName": "赵敏", "phone": "13800000004", "email": "zhaomin@haiyan.cn", "status": "1", "address": "宁波市北仑区大碶街道", "remark": "新开发客户，潜力大", "createdAt": "2026-05-16 14:00:00", "updatedAt": "2026-05-29 09:45:00"},
    {"id": 10005, "name": "光年网络科技有限公司", "contactName": "陈杰", "phone": "13800000005", "email": "chenjie@guangnian.dev", "status": "2", "address": "成都市高新区天府大道", "remark": "合同到期未续签", "createdAt": "2026-05-22 11:20:00", "updatedAt": "2026-05-25 17:30:00"},
    {"id": 10006, "name": "天穹数据技术有限公司", "contactName": "刘洋", "phone": "13800000006", "email": "liuyang@tianqiong.com", "status": "1", "address": "北京市海淀区上地信息产业基地", "remark": "重点客户，需要定期跟进", "createdAt": "2026-05-10 09:10:00", "updatedAt": "2026-05-29 10:00:00"},
    {"id": 10007, "name": "碧波生态农业集团", "contactName": "周婷", "phone": "13800000007", "email": "zhouting@bibo.agri", "status": "1", "address": "昆明市盘龙区北京路", "remark": "首次合作，试用阶段", "createdAt": "2026-05-15 13:40:00", "updatedAt": "2026-05-28 08:15:00"},
    {"id": 10008, "name": "墨白文化传媒有限公司", "contactName": "黄磊", "phone": "13800000008", "email": "hundlei@mobai.cn", "status": "2", "address": "长沙市岳麓区梅溪湖", "remark": "业务调整中", "createdAt": "2026-05-03 16:00:00", "updatedAt": "2026-05-18 12:00:00"},
]

_next_id = 10009

def _get_next_id():
    global _next_id
    _next_id += 1
    return _next_id

# --- models ---
class CustomerCreate(BaseModel):
    name: str
    contactName: str
    phone: str
    email: str
    address: str = ""
    remark: str = ""

class CustomerUpdate(CustomerCreate):
    id: int

# --- endpoints ---
@router.get("/list")
def get_customer_list(
    name: str = None,
    status: str = None,
    startTime: str = None,
    endTime: str = None,
    current: int = 1,
    size: int = 20,
):
    result = copy.deepcopy(customers)
    if name:
        result = [c for c in result if name in c["name"]]
    if status:
        result = [c for c in result if c["status"] == status]
    if startTime:
        result = [c for c in result if c["createdAt"][:10] >= startTime]
    if endTime:
        result = [c for c in result if c["createdAt"][:10] <= endTime]
    total = len(result)
    start = (current - 1) * size
    end = start + size
    return {"code": 200, "msg": "success", "data": {
        "records": result[start:end],
        "current": current,
        "size": size,
        "total": total,
    }}

@router.post("/create")
def add_customer(params: CustomerCreate):
    c = {"id": _get_next_id(), **params.model_dump(), "createdAt": "2026-05-30 12:00:00", "updatedAt": "2026-05-30 12:00:00"}
    customers.append(c)
    return {"code": 200, "msg": "新增成功", "data": c}

@router.put("/update")
def edit_customer(params: CustomerUpdate):
    data = params.model_dump()
    for i, c in enumerate(customers):
        if c["id"] == data["id"]:
            data["createdAt"] = c["createdAt"]
            data["updatedAt"] = "2026-05-30 12:00:00"
            customers[i] = data
            return {"code": 200, "msg": "更新成功", "data": data}
    return {"code": 404, "msg": "客户不存在", "data": None}

@router.delete("/delete")
def remove_customer(id: int):
    global customers
    before = len(customers)
    customers = [c for c in customers if c["id"] != id]
    if before != len(customers):
        return {"code": 200, "msg": "删除成功", "data": None}
    return {"code": 404, "msg": "客户不存在", "data": None}
