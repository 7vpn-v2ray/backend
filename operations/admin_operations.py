import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

import execptions
from db import Admin
from schema._input import adminLoginModel, updateAdminInfoByUsernameModel
from utils.jwtHandlerClass import JWTHandler, JWTResponsePayload
from utils.secrets import passwordManager


class adminOperation:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def getAdminInfoByUsername(self, username: str, route: str = "NOTSET!") -> Admin:
        query = sa.select(Admin).where(Admin.username == username)
        async with self.db_session as session:
            admin_data = await session.scalar(query)
        if admin_data is None:
            raise execptions.userNotFound(route)
        return admin_data

    async def updateAdminInfoByUsername(self, data: updateAdminInfoByUsernameModel, username: str, clientIp: str,
                                        route: str = "NOTSET!") -> {}:
        adminInfo = await self.getAdminInfoByUsername(username, route)

        if adminInfo is None:
            raise execptions.adminNotFound(route)

        update_fields = data.model_dump(exclude_unset=True)
        if "password" in update_fields:
            update_fields["password"] = passwordManager.hash(update_fields.pop("password"))

        if not update_fields:
            return {"status": False, "error": "No changes provided"}

        update_query = (
            sa.update(Admin)
            .where(Admin.username == username)
            .values(**update_fields)
        )
        async with self.db_session as session:
            await session.execute(update_query)
            await session.commit()

        if "username" in update_fields:
            return JWTHandler.generate(username=update_fields['username'], client_ip=clientIp)
        else:
            return {"status": True}

    async def login(self, clientIp: str, data: adminLoginModel, route: str = "NOTSET!") -> JWTResponsePayload:
        username = data.username
        password = data.password

        userInfo = await self.getAdminInfoByUsername(username, route)
        if userInfo is None:
            raise execptions.userNotFound(route)

        if not passwordManager.verify(password, userInfo.password):
            raise execptions.userOrPasswordIncorrect(route)
        return JWTHandler.generate(username=username, client_ip=clientIp)
