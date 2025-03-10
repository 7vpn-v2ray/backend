import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

import execptions
from db import Group
from schema._input import newGroupModel, updateGroupInfoByNameModel


class adminGroupsOperations:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def createNewGroup(self, data: newGroupModel, route: str = "NOT SET!") -> {}:
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

    async def getGroupInfoByName(self, name: str, route: str = "NOTSET!") -> list[Group]:
        if name is None :
            query = sa.select(Group)
        else:
            query = sa.select(Group).where(Group.name == name)

        async with self.db_session as session:
            groupData = await session.execute(query)
            groups = groupData.fetchall()

        if not groups:
            raise execptions.groupNotFound(route)

        return [group._asdict()['Group'] for group in groups]

    async def getGroupInfoById(self, id: int, route: str = "NOTSET!") -> list[Group]:
        if id is None:
            query = sa.select(Group)
        else:
            query = sa.select(Group).where(Group.id == id)
        async with self.db_session as session:
            groupData = await session.execute(query)
            groups = groupData.fetchall()

        if groupData is None:
            raise execptions.groupNotFound(route)
        return [group._asdict()['Group'] for group in groups]

    async def updateGroupInfoByName(self, data: updateGroupInfoByNameModel, groupName: str,
                                    route: str = "NOTSET!") -> {}:
        await self.getGroupInfoByName(groupName, route)

        update_fields = data.model_dump(exclude_unset=True)
        if not update_fields:
            return {"status": False, "error": "No changes provided"}

        update_query = (
            sa.update(Group)
            .where(Group.name == groupName)
            .values(**update_fields)
        )
        async with self.db_session as session:
            await session.execute(update_query)
            await session.commit()

        return {"status": True}

    async def deleteGroupByName(self, groupName: str, route: str = "NOTSET!") -> bool:
        await self.getGroupInfoByName(groupName, route)
        delete_query = (
            sa.delete(Group).where(Group.name == groupName)
        )
        async with self.db_session as session:
            await session.execute(delete_query)
            await session.commit()
        return True

    async def isGroupExist(self, groupName):
        query = sa.select(Group).where(Group.name == groupName)
        async with self.db_session as session:
            user_data = await session.scalar(query)
            if user_data is None:
                return False
            return True
