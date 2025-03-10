from typing import Annotated

from fastapi import APIRouter, Body
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import get_db
from operations.groups_operations import adminGroupsOperations
from schema._input import newGroupModel, updateGroupInfoByNameModel
from schema.jwt import JWTPayload
from utils.jwtHandlerClass import JWTHandler

admin_groups_router = APIRouter()


@admin_groups_router.post("/new_group")
async def newGroup(db_session: Annotated[AsyncSession, Depends(get_db)],
                   data: newGroupModel = Body(),
                   tokenData: JWTPayload = Depends(JWTHandler.verify_token)):
    return await adminGroupsOperations(db_session).createNewGroup(data, "/new_group")


@admin_groups_router.put("/update_group")
async def updateAdminInfo(db_session: Annotated[AsyncSession, Depends(get_db)],
                          data: updateGroupInfoByNameModel = Body(),
                          groupName: str = Body(),
                          tokenData: JWTPayload = Depends(JWTHandler.verify_token)):
    return await adminGroupsOperations(db_session).updateGroupInfoByName(data, groupName, "/update_group")


@admin_groups_router.get("/get_group")
async def getGroupInfoByName(db_session: Annotated[AsyncSession, Depends(get_db)],
                             groupName: str = None,
                             tokenData: JWTPayload = Depends(JWTHandler.verify_token)):
    return await adminGroupsOperations(db_session).getGroupInfoByName(groupName, "/get_group")


@admin_groups_router.get("/get_group_by_id")
async def getGroupInfoByName(db_session: Annotated[AsyncSession, Depends(get_db)],
                             groupId: int,
                             tokenData: JWTPayload = Depends(JWTHandler.verify_token)):
    return await adminGroupsOperations(db_session).getGroupInfoById(groupId, "/get_group_by_id")


@admin_groups_router.delete("/delete_group")
async def getAdminInfo(db_session: Annotated[AsyncSession, Depends(get_db)],
                       groupName: str,
                       tokenData: JWTPayload = Depends(JWTHandler.verify_token)):
    return await adminGroupsOperations(db_session).deleteGroupByName(groupName, "/delete_group")
