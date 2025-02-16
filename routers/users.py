from fastapi import APIRouter, Body, Request, Header
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from operations.users import UsersOperation
from db.engine import get_db
from schema._input import userInputModel, updateUserInfoByUsernameModel, userLoginModel
from schema.jwt import JWTPayload
from utils.jwtHandlerClass import JWTHandler

router = APIRouter()


@router.post("/register")
async def register(
        db_session: Annotated[AsyncSession, Depends(get_db)],
        auth_token: Annotated[str, Header()],
        request: Request,
        data: userInputModel = Body(),
):
    JWTHandler.verify_token(request=request, auth_token=auth_token)

    user = await UsersOperation(db_session).create(
        username=data.username,
        password=data.password,
        route="/register"
    )
    return user


@router.post("/login")
async def login(db_session: Annotated[AsyncSession, Depends(get_db)],
                request: Request,
                data: userLoginModel = Body()):
    client_ip = request.client.host
    return await UsersOperation(db_session).login(client_ip, data, "/login")


@router.put("/update_userinfo/")
async def update_username(db_session: Annotated[AsyncSession, Depends(get_db)],
                          data: updateUserInfoByUsernameModel = Body(),
                          ):
    user = await UsersOperation(db_session).updateUserInfoByUsername(data, "/update_userinfo")
    return user


@router.delete("/delete_user")
async def deleteUserByUsername(
        db_session: Annotated[AsyncSession, Depends(get_db)],
        tokenData: JWTPayload = Depends(JWTHandler.verify_token),
):
    return await UsersOperation(db_session).deleteUserByUsername(tokenData.username, "/delete_user")


@router.get("/getInfo/{username}{password}")
async def get_info(db_session: Annotated[AsyncSession, Depends(get_db)],
                   username: str,
                   password: str
                   ):
    user = await UsersOperation(db_session).getUserInfoByUsername(
        username=username,
        password=password,
        route="/getInfo"
    )
    return user
