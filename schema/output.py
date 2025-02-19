from pydantic import BaseModel
from uuid import UUID

class registerOutput(BaseModel):
    username: str
    id: UUID
class updateUsername(BaseModel):
    status : bool
    access : str
