import json, os, jwt, datetime
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import init_db, get_session, User, Role, MenuResource, RoleMenuResource
from routers.business.customer import router as customer_router
from routers.system.user import router as user_router
from routers.system.role import router as role_router

JWT_SECRET = "art-design-dev-secret-key"
JWT_ALGO = "HS256"

app = FastAPI(title="Art Design Pro Backend", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(customer_router)
app.include_router(user_router)
app.include_router(role_router)


# --- on startup ---
@app.on_event("startup")
def startup():
    init_db()
    # Auto-seed if no users
    db = get_session()
    if db.query(User).count() == 0:
        db.close()
        import seed
        seed.seed()
    else:
        db.close()
    print("DB ready")


# --- helpers ---
def get_current_user(authorization: str = Header(""), db: Session = Depends(get_session)):
    if not authorization:
        raise HTTPException(401, "未授权")
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        user = db.query(User).get(payload["userId"])
        if not user:
            raise HTTPException(401, "用户不存在")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "令牌过期")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "无效令牌")


# --- auth ---
@app.post("/api/auth/login")
def login(body: dict):
    db = get_session()
    user = db.query(User).filter_by(userName=body.get("userName", "")).first()
    if not user or user.password != body.get("password", ""):
        db.close()
        return {"code": 400, "msg": "用户名或密码错误", "data": None}
    role_codes = [r.roleCode for r in user.roles]
    token = jwt.encode({
        "userId": user.id,
        "roles": role_codes,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, JWT_SECRET, algorithm=JWT_ALGO)
    refresh = jwt.encode({"userId": user.id}, JWT_SECRET + "_refresh", algorithm=JWT_ALGO)
    db.close()
    return {"code": 200, "msg": "success", "data": {
        "token": token, "refreshToken": refresh
    }}


@app.get("/api/user/info")
def get_user_info(authorization: str = Header("")):
    if not authorization:
        return {"code": 401, "msg": "未授权", "data": None}
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except:
        return {"code": 401, "msg": "无效令牌", "data": None}
    db = get_session()
    user = db.query(User).get(payload["userId"])
    if not user:
        db.close()
        return {"code": 401, "msg": "用户不存在", "data": None}
    role_codes = [r.roleCode for r in user.roles]
    # Collect all auth marks across all roles
    all_buttons = set()
    for role in user.roles:
        for rmr in db.query(RoleMenuResource).filter_by(roleId=role.id).all():
            if rmr.authMarks:
                marks = json.loads(rmr.authMarks)
                all_buttons.update(marks)
    buttons = list(all_buttons)
    db.close()
    return {"code": 200, "msg": "success", "data": {
        "buttons": buttons,
        "roles": role_codes,
        "userId": user.id,
        "userName": user.userName,
        "email": user.userEmail,
        "avatar": user.avatar or "https://api.dicebear.com/7.x/avataaars/svg?seed=" + user.userName,
    }}


# --- menus (backend mode core) ---
MENU_CACHE = {}
MENU_CACHE_TIME = 0

def build_tree(parent_id, db):
    items = db.query(MenuResource).filter_by(parentId=parent_id).order_by(MenuResource.sort).all()
    result = []
    for m in items:
        meta = json.loads(m.meta) if m.meta else {}
        # Remove authList from meta - it will be in separate marks
        meta.pop("authList", None)
        node = {
            "name": m.name,
            "path": m.path if m.path else "",
            "component": m.component if m.component else "",
            "meta": meta,
        }
        children = build_tree(m.id, db)
        if children:
            node["children"] = children
        result.append(node)
    return result

@app.get("/api/v3/system/menus")
def get_menus(authorization: str = Header("")):
    if not authorization:
        return {"code": 401, "msg": "未授权", "data": None}
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except:
        return {"code": 401, "msg": "无效令牌", "data": None}
    db = get_session()
    user = db.query(User).get(payload["userId"])
    if not user:
        db.close()
        return {"code": 401, "msg": "用户不存在", "data": None}
    role_ids = [r.id for r in user.roles]
    # Get menu resource IDs for this user's roles
    rows = db.query(RoleMenuResource.menuResourceId).filter(
        RoleMenuResource.roleId.in_(role_ids)
    ).distinct().all()
    allowed_ids = set(r[0] for r in rows)
    # Get top-level menus that are allowed or have children that are allowed
    all_menus = db.query(MenuResource).order_by(MenuResource.sort).all()
    allowed_set = set()
    for m in all_menus:
        if m.id in allowed_ids:
            allowed_set.add(m.id)
            # Also allow parent chain
            p = m.parentId
            while p:
                allowed_set.add(p)
                p = next((x.parentId for x in all_menus if x.id == p), None)
    # Build tree
    def _build(pid):
        items = [m for m in all_menus if m.parentId == pid and m.id in allowed_set]
        result = []
        for m in items:
            meta = json.loads(m.meta) if m.meta else {}
            meta.pop("authList", None)
            # Get authMarks for this menu from the role's assignment
            rmr = db.query(RoleMenuResource).filter(
                RoleMenuResource.roleId.in_(role_ids),
                RoleMenuResource.menuResourceId == m.id
            ).first()
            if rmr and rmr.authMarks:
                marks = json.loads(rmr.authMarks)
                if marks:
                    meta["authList"] = [{"title": x, "authMark": x} for x in marks]
            node = {
                "name": m.name,
                "path": m.path or "",
                "component": m.component or "",
                "meta": meta,
            }
            children = _build(m.id)
            if children:
                node["children"] = children
            result.append(node)
        return result
    tree = _build(None)
    db.close()
    return {"code": 200, "msg": "success", "data": tree}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
