import uvicorn
from fastapi import FastAPI

from db.engine import Base, engine
from routers.admin_groups_routers import admin_groups_router
from routers.admin_routers import admin_router
from routers.admin_users_routers import admin_user_routers

app = FastAPI()


@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(admin_router, prefix="/admin")
# app.include_router(admin_user_routers, prefix="/admin/user")
app.include_router(admin_groups_router, prefix="/admin/groups")

if __name__ == "__main__":
    uvicorn.run(app)
#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDEwMDE3NjksInVzZXJuYW1lIjoiYWRtaW4iLCJpcCI6IjEyNy4wLjAuMSJ9.NdxlyCCLoJSfRzykvvND_VglMHWb8fv24_2H-UiNpGU