from fastapi import APIRouter, Body, Request, Header
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from db.engine import get_db
from operations.groups_operations import adminGroupsOperations
from schema._input import adminLoginModel, updateAdminInfoByUsernameModel, newGroupModel
from schema.jwt import JWTPayload
from utils.jwtHandlerClass import JWTHandler

admin_groups_router = APIRouter()


@admin_groups_router.post("/new_group")
async def newGroup(db_session: Annotated[AsyncSession, Depends(get_db)],
                auth_token: Annotated[str, Header()],
                data: newGroupModel = Body(),
                tokenData: JWTPayload = Depends(JWTHandler.verify_token)):
    return await adminGroupsOperations(db_session).createNewGroup(data, "/new_group")





@admin_groups_router.get("/get_group{group_name}")
async def getGroupInfoByName(db_session: Annotated[AsyncSession, Depends(get_db)],
                       auth_token: Annotated[str, Header()],
                       groupName : str,
                       tokenData: JWTPayload = Depends(JWTHandler.verify_token)):
    # JWTHandler.verify_token(request=request, auth_token=auth_token)
    return await adminGroupsOperations(db_session).getGroupInfoByName(groupName, "/get_info")
