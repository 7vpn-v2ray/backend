import itertools

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

import execptions
from db.models import User
from operations.groups_operations import adminGroupsOperations
from routers.admin_groups_routers import getGroupInfoByName
from schema._input import updateUserInfoByUsernameModel, userInputModel, userDetails
from utils.secrets import passwordManager
from datetime import datetime, timedelta



class usersOperation:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create(self, data: userInputModel, route: str = "NOTSET!") -> None:
        username = data.username
        password = data.password

        if await self.isUserNameExist(username):
            raise execptions.userExisted(route)

        admin_groups_operations = adminGroupsOperations(db_session=self.db_session)

        user = User(**data.__dict__)  # Initial user object
        user_details = userDetails(**user.__dict__)  # Convert to userDetails model
        # groupInfo_dict = dict(itertools.zip_longest(*[iter(groupInfo)] * 2, fillvalue=""))
        groupInfo = await admin_groups_operations.getGroupInfoById(id=user_details.group_id, route=route)
        if not groupInfo:
             raise Exception("Group not found!")

        # فرض بر اینه که groupInfo یه لیست از دیکشنری‌هاست
        groupInfo_dict = groupInfo[0]

        user_details_dict = user_details.dict() if hasattr(user_details, "dict") else user_details.__dict__
        # Update values from groupInfo if they are "-1"
        updated_values = {
            key: getattr(groupInfo_dict, key, value)
            if value in (None, -1, -1.0, "-1", "-1.0", "")
            else value
            for key, value in user_details_dict.items()
        }

        updated_values['relative_expire_date'] = "-1"
        # Set hashed password in the updated values
        updated_values["password"] = passwordManager.hash(password)
        updated_values["username"] = username
        updated_values["group_name"] = groupInfo_dict.name

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
        if username in (None, "undefined", ""):
            query = sa.select(User)
        else:
            query = sa.select(User).where(User.username == username)

        async with self.db_session as session:
            result = await session.execute(query)
            users: User = result.scalars().all()

        if not users:
            if username is None:
                users=[]
            else:
             raise execptions.userNotFound(route)

        for user in users:
            await self.calculateUserExpireDate(user, route)  # in-place

        return users

    async def getUserInfoByUsernameAndPassword(
            self,
            username: str,
            password: str,
            route: str = "NOTSET!"
    ) -> User:
        if not username or username in ("undefined", ""):
            raise execptions.userNotFound(route)

        query = sa.select(User).where(User.username == username)

        async with self.db_session as session:
            result = await session.execute(query)
            user = result.scalar_one_or_none()

        if not user:
            raise execptions.userNotFound(route)

        if not passwordManager.verify(password, user.password):
            raise execptions.invalidCredentials(route)

        user = await self.calculateUserExpireDate(user,route)
        user.password = password

        return user

    async def calculateUserExpireDate(self,user,route="NOTSET"):
        if user.first_login == "-1":
            user.relative_expire_date = "-1"
        elif (user.relative_expire_date == "-1" or user.relative_expire_date == ""):
            try:
                first_login_date = datetime.strptime(user.first_login, "%Y-%m-%d")

                group_data = await getGroupInfoByName(db_session=self.db_session,groupId=user.group_id)
                days_to_add = int(group_data[0].relative_expire_date)

                expire_date = first_login_date + timedelta(days=days_to_add)

                user.relative_expire_date = expire_date.strftime("%Y-%m-%d")

            except Exception as e:
                raise execptions.invalidCredentials(f"{route} - Date parse error: {e}")
        return user
    async def isUserNameExist(self, username: str) -> bool:
        query = sa.select(User).where(User.username == username)
        async with self.db_session as session:
            user_data = await session.scalar(query)
            if user_data is None:
                return False
            return True


    async def isUserIdExist(self, userId: int) -> bool:
        query = sa.select(User).where(User.id == userId)
        async with self.db_session as session:
            user_data = await session.scalar(query)
            if user_data is None:
                return False
            return True


    async def updateUserInfoByUsername(self, data: updateUserInfoByUsernameModel, username: str,
                                       route: str = "NOTSET!") -> {}:
        if not await self.isUserNameExist(username):
            raise execptions.userNotFound(route)

        if await self.isUserNameExist(data.username):
            raise execptions.userExisted(route)

        update_fields = data.model_dump(exclude_unset=True)
        user_old_data = await self.getUserInfoByUsername(username, route)
        user_old_data = user_old_data[0]

        if not update_fields:
            return {"status": False, "error": "No changes provided"}

        if "password" in update_fields:
            update_fields["password"] = passwordManager.hash(update_fields.pop("password"))

        if 'relative_expire_date' in update_fields and (update_fields['relative_expire_date'] == '' or user_old_data.first_login == "-1"):
            update_fields['relative_expire_date'] = "-1"
        if 'first_login' in update_fields and update_fields['first_login'] == '':
            update_fields['first_login'] = "-1"
        print(update_fields)
        update_query = (
            sa.update(User)
            .where(User.username == username)
            .values(**update_fields)
        )
        async with self.db_session as session:
            await session.execute(update_query)
            await session.commit()

    async def updateUserInfoByUserId(self, data: updateUserInfoByUsernameModel, userId: int,
                                       route: str = "NOTSET!") -> {}:
        if not await self.isUserIdExist(userId):
            raise execptions.userNotFound(route)

        if await self.isUserNameExist(data.username):
            raise execptions.userExisted(route)

        update_fields = data.model_dump(exclude_unset=True)

        if not update_fields:
            return {"status": False, "error": "No changes provided"}

        if "password" in update_fields:
            update_fields["password"] = passwordManager.hash(update_fields.pop("password"))

        update_query = (
            sa.update(User)
            .where(User.id == userId)
            .values(**update_fields)
        )
        async with self.db_session as session:
            await session.execute(update_query)
            await session.commit()

    async def deleteUserByUsername(self, username: str, route: str = "NOTSET!") -> bool:
        if not await self.isUserNameExist(username):
            raise execptions.userNotFound(route)
        delete_query = (
            sa.delete(User).where(User.username == username)
        )
        async with self.db_session as session:
            await session.execute(delete_query)
            await session.commit()
        return True
    async def used_traffic(self, username: str,traffic : float, route: str = "NOTSET!") -> bool:
        data = await self.getUserInfoByUsername(username)
        current_traffic = data[0].traffic
        new_traffic = current_traffic - traffic
        if new_traffic <= 0:
            new_traffic = 0
        data = {"traffic": new_traffic}
        data = updateUserInfoByUsernameModel(**data)
        await self.updateUserInfoByUsername(data=data,username=username,route=route)
        return True
