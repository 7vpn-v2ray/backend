from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
import sqlalchemy as sa
from execptions import userNotFound

from schema._input import updateUserInfoByUsernameModel, userInputModel


class UsersOperation:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create(self, username: str, password: str) -> User:
        user = User(username=username, password=password)

        async with self.db_session as session:
            session.add(user)
            await session.commit()

        return user

    async def getUserInfoByUsername(self, username: str, password: str,route :str = "NOTSET!") -> User:
        query = sa.select(User).where((User.username == username) & (User.password == password))
        async with self.db_session as session:
            user_data = await session.scalar(query)
            if user_data is None:
                raise userNotFound(route)
            return user_data

    async def isUserExist(self, username: str) -> bool:
        query = sa.select(User).where(User.username == username)
        async with self.db_session as session:
            user_data = await session.scalar(query)
            if user_data is None:
                return False
            return True

    async def updateUserInfoByUsername(self, data: updateUserInfoByUsernameModel) -> None:

        username = data.username
        newUsername = data.newUsername
        password = data.password
        newPassword = data.get_final_password()

        userInfo = await self.getUserInfoByUsername(username,password,"/update_userinfo")

        if userInfo is None:
            raise userNotFound("/update_userinfo")
        newUsernameInfo = await self.isUserExist(newUsername)
        if newUsernameInfo is True and username != newUsername:
            raise "Username already exists"
        update_query = (
            sa.update(User)
            .where((User.username == username) & (User.password == password))
            .values(username=newUsername, password=newPassword)
        )
        async with self.db_session as session:
            await session.execute(update_query)
            await session.commit()

    async def deleteUserByUsername(self, data: userInputModel) -> bool:
        username = data.username
        password = data.password
        userInfo = await self.getUserInfoByUsername(username, password)
        if userInfo is None:
            raise "User not found delete"
        delete_query = (
            sa.delete(User).where((User.username == username) & (User.password == password))
        )
        async with self.db_session as session:
            await session.execute(delete_query)
            await session.commit()
        return True
