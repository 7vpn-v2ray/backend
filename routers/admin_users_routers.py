from fastapi import APIRouter, Body, Request, Header
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from operations.users_operations import usersOperation
from db.engine import get_db
from schema._input import userInputModel, updateUserInfoByUsernameModel, adminLoginModel, userDelete
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

@admin_user_routers.put("/update_userinfo/")
async def update_username(db_session: Annotated[AsyncSession, Depends(get_db)],
                          auth_token: Annotated[str, Header()],
                          request: Request,
                          data: updateUserInfoByUsernameModel = Body(),
                          ):
    user = await usersOperation(db_session).updateUserInfoByUsername(data, "/update_userinfo")
    return user


@admin_user_routers.delete("/delete_user")
async def deleteUserByUsername(
        db_session: Annotated[AsyncSession, Depends(get_db)],
        auth_token: Annotated[str, Header()],
        request: Request,
        data: userDelete = Body(),
        tokenData: JWTPayload = Depends(JWTHandler.verify_token)
):
    return await usersOperation(db_session).deleteUserByUsername(data.username, "/delete_user")


@admin_user_routers.get("/getInfo/{username}")
async def get_info(db_session: Annotated[AsyncSession, Depends(get_db)],
                   auth_token: Annotated[str, Header()],
                   request: Request,
                   username: str
                   ):
    user = await usersOperation(db_session).getUserInfoByUsername(
        username=username,
        route="/getInfo"
    )
    return user
