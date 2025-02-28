from typing import Annotated

from fastapi import APIRouter, Body, Request, Header
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import get_db
from operations.admin_operations import adminOperation
from schema._input import adminLoginModel, updateAdminInfoByUsernameModel
from schema.jwt import JWTPayload
from utils.jwtHandlerClass import JWTHandler

admin_router = APIRouter()


@admin_router.post("/login")
async def login(db_session: Annotated[AsyncSession, Depends(get_db)],
                request: Request,
                data: adminLoginModel = Body()):
    client_ip = request.client.host
    return await adminOperation(db_session).login(client_ip, data, "/login")


@admin_router.post("/update_info")
async def updateAdminInfo(db_session: Annotated[AsyncSession, Depends(get_db)],
                          auth_token: Annotated[str, Header()],
                          request: Request,
                          data: updateAdminInfoByUsernameModel = Body(),
                          tokenData: JWTPayload = Depends(JWTHandler.verify_token)):
    # JWTHandler.verify_token(request=request, auth_token=auth_token)
    return await adminOperation(db_session).updateAdminInfoByUsername(data, tokenData.username, request.client.host,
                                                                      "/update_info")


@admin_router.get("/get_info")
async def getAdminInfo(db_session: Annotated[AsyncSession, Depends(get_db)],
                       auth_token: Annotated[str, Header()],
                       request: Request,
                       tokenData: JWTPayload = Depends(JWTHandler.verify_token)):
    # JWTHandler.verify_token(request=request, auth_token=auth_token)
    return await adminOperation(db_session).getAdminInfoByUsername(tokenData.username, "/get_info")
