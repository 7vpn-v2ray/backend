from uuid import UUID

from pydantic import BaseModel


class registerOutput(BaseModel):
    username: str
    id: UUID


class updateUsername(BaseModel):
    status: bool
    access: str
