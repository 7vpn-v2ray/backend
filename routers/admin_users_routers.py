from typing import Annotated

from fastapi import APIRouter, Body, Request, Header
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import get_db
from operations.users_operations import usersOperation
from schema._input import userInputModel, updateUserInfoByUsernameModel, userDelete
from schema.jwt import JWTPayload
from utils.jwtHandlerClass import JWTHandler

admin_user_routers = APIRouter()


@admin_user_routers.post("/new_user")
async def register(
        db_session: Annotated[AsyncSession, Depends(get_db)],
        auth_token: Annotated[str, Header()],
        request: Request,
        tokenData: JWTPayload = Depends(JWTHandler.verify_token),
        data: userInputModel = Body(),
):
    user = await usersOperation(db_session).create(
        data=data,
        route="/new_user"
    )
    return user


@admin_user_routers.put("/update_userinfo_by_username/")
async def update_username(db_session: Annotated[AsyncSession, Depends(get_db)],
                          auth_token: Annotated[str, Header()],
                          request: Request,
                          data: updateUserInfoByUsernameModel = Body(),
                          username=Body()
                          ):
    user = await usersOperation(db_session).updateUserInfoByUsername(data, username, "/update_userinfo_by_username")
    return user

@admin_user_routers.put("/update_userinfo_by_userid/")
async def update_username(db_session: Annotated[AsyncSession, Depends(get_db)],
                          auth_token: Annotated[str, Header()],
                          request: Request,
                          data: updateUserInfoByUsernameModel = Body(),
                          user_id :int =Body()
                          ):
    user = await usersOperation(db_session).updateUserInfoByUserId(data, user_id, "/update_userinfo_by_userid")
    return user
@admin_user_routers.put("/used_traffic/")
async def used_traffic(db_session: Annotated[AsyncSession, Depends(get_db)],
                   auth_token: Annotated[str, Header()],
                   username: str,
                   traffic: float,
                   tokenData: JWTPayload = Depends(JWTHandler.verify_token)
                   ):
    await usersOperation(db_session).used_traffic(
        username=username,
        traffic=traffic,
        route="/usedTraffic"
    )
@admin_user_routers.delete("/delete_user")
async def deleteUserByUsername(
        db_session: Annotated[AsyncSession, Depends(get_db)],
        auth_token: Annotated[str, Header()],
        data: userDelete = Body(),
        tokenData: JWTPayload = Depends(JWTHandler.verify_token)
):
    return await usersOperation(db_session).deleteUserByUsername(data.username, "/delete_user")


@admin_user_routers.get("/getInfo")
async def get_info(db_session: Annotated[AsyncSession, Depends(get_db)],
                   auth_token: Annotated[str, Header()],
                   username: str=None,
                   tokenData: JWTPayload = Depends(JWTHandler.verify_token)
                   ):
    user = await usersOperation(db_session).getUserInfoByUsername(
        username=username,
        route="/getInfo"
    )
    return user

@admin_user_routers.get("/getInfoApp")
async def get_info(db_session: Annotated[AsyncSession, Depends(get_db)],
                   auth_token: Annotated[str, Header()],
                   username: str,
                   password: str,
                   tokenData: JWTPayload = Depends(JWTHandler.verify_token)
                   ):
    user = await usersOperation(db_session).getUserInfoByUsernameAndPassword(
        username=username,
        password=password,
        route="/getInfoApp"
    )
    return user

