import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from db.engine import Base, engine
from routers.admin_groups_routers import admin_groups_router
from routers.admin_routers import admin_router
from routers.admin_users_routers import admin_user_routers

# مسیر پوشه build Vite
# FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "dist")
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist"))

print(">>> FRONTEND_DIST =", FRONTEND_DIST)  # Debug

# Mount کردن assets
assets_path = os.path.join(FRONTEND_DIST, "assets")
print(">>> ASSETS PATH =", assets_path)  # Debug

app = FastAPI(
    title="My API",
    description="API Documentation",
    version="1.0",
    docs_url="/docs",
)

# CORS config
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8090",
    "https://paneltest.hiteck.ir",
    "https://paneltest.hiteck.ir:8090",
    "https://127.0.0.1:8090",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory=assets_path), name="assets")


# Database init
@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Routers
app.include_router(admin_router, prefix="/admin")
app.include_router(admin_user_routers, prefix="/admin/users")
app.include_router(admin_groups_router, prefix="/admin/groups")

# --- سرو کردن SPA ---
@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa(full_path: str):
    return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)
