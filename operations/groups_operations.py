from sqlalchemy.ext.asyncio import AsyncSession

from db import Group
import sqlalchemy as sa
import execptions
from utils.secrets import passwordManager
from schema._input import adminLoginModel, updateAdminInfoByUsernameModel, newGroupModel
from utils.jwtHandlerClass import JWTHandler,JWTResponsePayload


class adminGroupsOperations:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session


    async def createNewGroup(self,data : newGroupModel , route:str = "NOT SET!") -> {}:
        groupName = data.name

        if await self.isGroupExist(groupName):
            raise execptions.groupExisted(route)
        insert_query = (
            sa.insert(Group)
            .values(
                name=groupName,
                relative_expire_date=data.relative_expire_date,
                multi_login=data.multi_login,
                traffic=data.traffic
            ).returning(Group)
        )

        async with self.db_session as session:
            result = await session.execute(insert_query)
            await session.commit()
            inserted_group = result.fetchone()._asdict()
        return inserted_group['Group']

    async def getGroupInfoByName(self, name: str, route: str = "NOTSET!") -> Group:
        query = sa.select(Group).where(Group.name == name)
        async with self.db_session as session:
            groupData = await session.scalar(query)
        if groupData is None:
            raise execptions.groupNotFound(route)
        return groupData

    async def deleteGroupByName(self, groupName : str, route: str = "NOTSET!") -> bool:
        await self.getGroupInfoByName(groupName,route)
        delete_query = (
            sa.delete(Group).where(Group.name == groupName)
        )
        async with self.db_session as session:
            await session.execute(delete_query)
            await session.commit()
        return True

    async def isGroupExist(self,groupName):
        query = sa.select(Group).where(Group.name == groupName)
        async with self.db_session as session:
            user_data = await session.scalar(query)
            if user_data is None:
                return False
            return True
