import json
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Art Design Pro Backend", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- include routers ---
from routers.business.customer import router as customer_router
from routers.system.user import router as user_router
from routers.system.role import router as role_router

app.include_router(customer_router)
app.include_router(user_router)
app.include_router(role_router)


# --- auth ---
@app.post("/api/auth/login")
def login():
    return {"code": 200, "msg": "success", "data": {
        "token": "mock-token-admin",
        "refreshToken": "mock-refresh-token",
    }}


# --- menu (reads from menu.json) ---
_menu_cache = None
_menu_mtime = None

@app.get("/api/v3/system/menus")
def get_menus():
    global _menu_cache, _menu_mtime
    path = os.path.join(os.path.dirname(__file__), "menu.json")
    mtime = os.path.getmtime(path)
    if _menu_mtime != mtime or _menu_cache is None:
        with open(path, "r", encoding="utf-8") as f:
            _menu_cache = json.load(f)
        _menu_mtime = mtime
    return {"code": 200, "msg": "success", "data": _menu_cache}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
