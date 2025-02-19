import uvicorn
from fastapi import FastAPI

from db.engine import Base, engine
from routers.admin_routers import admin_router
from routers.admin_users_routers import admin_user_routers

app = FastAPI()


@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(admin_router, prefix="/admin")
app.include_router(admin_user_routers, prefix="/admin/user")

if __name__ == "__main__":
    uvicorn.run(app)
#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDA4NDIwNDYsInVzZXJuYW1lIjoiYWRtaW4iLCJpcCI6IjEyNy4wLjAuMSJ9.76N0ceSguDozP4boKkRZhgV33Vv-56Kno6K8jl-vDPM