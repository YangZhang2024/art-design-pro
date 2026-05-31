from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import get_session, Customer

router = APIRouter(prefix="/api/customer", tags=["customer"])


class CustomerCreate(BaseModel):
    name: str
    contactName: str
    phone: str
    email: str
    address: str = ""
    remark: str = ""
    status: str

class CustomerUpdate(CustomerCreate):
    id: int


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@router.get("/list")
def get_customer_list(
    name: Optional[str] = None,
    status: Optional[str] = None,
    startTime: Optional[str] = None,
    endTime: Optional[str] = None,
    current: int = 1,
    size: int = 20,
):
    db = get_session()
    query = db.query(Customer)
    if name: query = query.filter(Customer.name.like(f"%{name}%"))
    if status: query = query.filter(Customer.status == status)
    if startTime: query = query.filter(Customer.createdAt >= startTime)
    if endTime: query = query.filter(Customer.createdAt <= endTime + " 23:59:59")
    total = query.count()
    rows = query.order_by(Customer.id.desc()).offset((current - 1) * size).limit(size).all()
    records = [{
        "id": r.id, "name": r.name, "contactName": r.contactName,
        "phone": r.phone, "email": r.email, "status": r.status,
        "address": r.address, "remark": r.remark,
        "createdAt": r.createdAt, "updatedAt": r.updatedAt,
    } for r in rows]
    db.close()
    return {"code": 200, "msg": "success", "data": {
        "records": records, "current": current, "size": size, "total": total,
    }}


@router.post("/create")
def add_customer(params: CustomerCreate):
    db = get_session()
    now = _now()
    c = Customer(**params.model_dump(), createdAt=now, updatedAt=now)
    db.add(c)
    db.commit()
    data = {k: str(v) if hasattr(v, "isoformat") else v
            for k, v in c.__dict__.items() if not k.startswith("_")}
    db.close()
    return {"code": 200, "msg": "新增成功", "data": data}


@router.put("/update")
def edit_customer(params: CustomerUpdate):
    db = get_session()
    c = db.query(Customer).get(params.id)
    if not c:
        db.close()
        return {"code": 404, "msg": "客户不存在", "data": None}
    for k, v in params.model_dump().items():
        if k != "id":
            setattr(c, k, v)
    c.updatedAt = _now()
    db.commit()
    data = {k: str(v) if hasattr(v, "isoformat") else v
            for k, v in c.__dict__.items() if not k.startswith("_")}
    db.close()
    return {"code": 200, "msg": "更新成功", "data": data}


@router.delete("/delete")
def remove_customer(id: int):
    db = get_session()
    c = db.query(Customer).get(id)
    if not c:
        db.close()
        return {"code": 404, "msg": "客户不存在", "data": None}
    db.delete(c)
    db.commit()
    db.close()
    return {"code": 200, "msg": "删除成功", "data": None}
