from typing import Optional

from pydantic import BaseModel


class userInputModel(BaseModel):
    username : str
    password : str

class updateUserInfoByUsernameModel(BaseModel):
    username: str
    password: str
    newUsername: str
    newPassword: Optional[str] = None

    def get_final_password(self) -> str:
        return self.newPassword if self.newPassword is not None else self.password
