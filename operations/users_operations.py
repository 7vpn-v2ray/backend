from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
import sqlalchemy as sa
import execptions
from operations.groups_operations import adminGroupsOperations
from utils.secrets import passwordManager
from schema._input import updateUserInfoByUsernameModel, userInputModel, adminLoginModel, userDetails
from schema.output import registerOutput
from utils.jwtHandlerClass import JWTHandler, JWTResponsePayload


class usersOperation:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create(self, data: userInputModel, route: str = "NOTSET!") -> None:
        username = data.username
        password = data.password

        if await self.isUserExist(username):
            raise execptions.userExisted(route)

        admin_groups_operations = adminGroupsOperations(db_session=self.db_session)

        user = User(**data.__dict__)  # Initial user object
        user_details = userDetails(**user.__dict__)  # Convert to userDetails model
        groupInfo = await admin_groups_operations.getGroupInfoById(id=user_details.group_id, route=route)
        groupInfo_dict = groupInfo.__dict__

        user_details_dict = user_details.dict() if hasattr(user_details, "dict") else user_details.__dict__
        # Update values from groupInfo if they are "-1"
        updated_values = {
            key: groupInfo_dict.get(key, value) if (str(value) == "-1" or str(value) == "-1.0") and value in (-1, "-1", -1.0,"-1.0") else value
            for key, value in user_details_dict.items()
        }

        print(updated_values)

        # Set hashed password in the updated values
        updated_values["password"] = passwordManager.hash(password)
        updated_values["username"] = username

        # Create the final user object with all updated values
        user = userInputModel(**updated_values)
        user = user.model_dump(exclude_unset=True)
        insert_query = (
            sa.insert(User)
            .values(**user).returning(User)
        )

        async with self.db_session as session:
            result = await session.execute(insert_query)
            await session.commit()
            inserted_user = result.fetchone()._asdict()
        return inserted_user['User']

    async def getUserInfoByUsername(self, username: str, route: str = "NOTSET!") -> User:

        query = sa.select(User).where(User.username == username)
        async with self.db_session as session:
            user_data = await session.scalar(query)
        if user_data is None:
            raise execptions.userNotFound(route)
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

    async def deleteUserByUsername(self, username: str, route: str = "NOTSET!") -> bool:
        if not await self.isUserExist(username):
            raise execptions.userNotFound(route)
        delete_query = (
            sa.delete(User).where(User.username == username)
        )
        async with self.db_session as session:
            await session.execute(delete_query)
            await session.commit()
        return True
