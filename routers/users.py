from fastapi import APIRouter, Body
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from operations.users import UsersOperation
from db.engine import get_db
from schema._input import userInputModel, updateUserInfoByUsernameModel

router = APIRouter()


@router.post("/register")
async def register(
        db_session: Annotated[AsyncSession, Depends(get_db)],
        data: userInputModel = Body(),
):
    user = await UsersOperation(db_session).create(
        username=data.username,
        password=data.password,
    )
    return user


@router.post("/login")
async def login():
    ...


@router.put("/update_userinfo/")
async def update_username(db_session: Annotated[AsyncSession, Depends(get_db)],
                          data: updateUserInfoByUsernameModel = Body(),
                          ):
    user = await UsersOperation(db_session).updateUserInfoByUsername(data)
    return user


@router.delete("/delete_user")
async def deleteUserByUsername(
        db_session: Annotated[AsyncSession, Depends(get_db)],
        data: userInputModel = Body(),
):
    return await UsersOperation(db_session).deleteUserByUsername(data)



@router.get("/getInfo/{username}{password}")
async def get_info(db_session: Annotated[AsyncSession, Depends(get_db)],
                   username: str,
                   password: str
                   ):
    user = await UsersOperation(db_session).getUserInfoByUsername(
        username=username,
        password=password
    )
    return user
