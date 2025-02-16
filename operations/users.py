from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
import sqlalchemy as sa
import execptions
from utils.secrets import passwordManager
from schema._input import updateUserInfoByUsernameModel, userInputModel, userLoginModel
from schema.output import registerOutput
from utils.jwtHandlerClass import JWTHandler,JWTResponsePayload

class UsersOperation:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create(self, username: str, password: str, route: str = "NOTSET!") -> registerOutput:

        if await self.isUserExist(username):
            raise execptions.userExisted(route)

        hashedPassword = passwordManager.hash(password)
        user = User(username=username, password=hashedPassword)
        async with self.db_session as session:
            session.add(user)
            await session.commit()

        return registerOutput(**user.__dict__)

    async def getUserInfoByUsername(self, username: str, password: str, route: str = "NOTSET!") -> User:
        query = sa.select(User).where(User.username == username)
        async with self.db_session as session:
            user_data = await session.scalar(query)
        if user_data is None:
            raise execptions.userNotFound(route)
        if not passwordManager.verify(password, user_data.password):
            raise execptions.userOrPasswordIncorrect(route)
        return user_data


    async def isUserExist(self, username: str) -> bool:
        query = sa.select(User).where(User.username == username)
        async with self.db_session as session:
            user_data = await session.scalar(query)
            if user_data is None:
                return False
            return True


    async def updateUserInfoByUsername(self, data: updateUserInfoByUsernameModel, route: str = "NOTSET!") -> None:
        username = data.username
        newUsername = data.newUsername
        password = data.password
        newPassword = data.get_final_password()

        userInfo = await self.getUserInfoByUsername(username, password, route)

        if userInfo is None:
            raise execptions.userNotFound(route)
        newUsernameInfo = await self.isUserExist(newUsername)
        if newUsernameInfo is True and username != newUsername:
            raise execptions.userExisted(route)
        update_query = (
            sa.update(User)
            .where(User.username == username)
            .values(username=newUsername, password=passwordManager.hash(newPassword))
        )
        async with self.db_session as session:
            await session.execute(update_query)
            await session.commit()


    async def deleteUserByUsername(self, data: userInputModel, route: str = "NOTSET!") -> bool:
        username = data.username
        password = data.password
        userInfo = await self.getUserInfoByUsername(username, password,route)
        if userInfo is None:
            raise execptions.userNotFound(route)
        delete_query = (
            sa.delete(User).where(User.username == username)
        )
        async with self.db_session as session:
            await session.execute(delete_query)
            await session.commit()
        return True


    async def login(self, clientIp : str,data: userLoginModel, route: str = "NOTSET!") -> JWTResponsePayload:
        username = data.username
        password = data.password

        userInfo = await self.getUserInfoByUsername(username, password,route)
        if userInfo is None:
            raise execptions.userNotFound(route)

        if not passwordManager.verify(password,userInfo.password):
            raise execptions.userOrPasswordIncorrect(route)
        return JWTHandler.generate(username=username,client_ip=clientIp)
