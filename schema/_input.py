from typing import Optional

from pydantic import BaseModel


class userInputModel(BaseModel):
    username: str
    password: str
    first_login: str = -1
    relative_expire_date: str = -1
    traffic: float = -1.0
    multi_login: int = -1
    group_id: int


class userDetails(BaseModel):
    group_id: int
    first_login: str = -1
    relative_expire_date: str = -1
    traffic: float = -1.0
    multi_login: int = -1


class updateUserInfoByUsernameModel(BaseModel):
    username: str = None
    password: Optional[str] = None
    first_login: Optional[str] = None
    relative_expire_date: Optional[str] = None
    traffic: Optional[float] = None
    multi_login: Optional[int] = None
    group_id: Optional[int] = None

    def get_final_password(self) -> str:
        return self.newPassword if self.newPassword is not None else self.password


class adminLoginModel(BaseModel):
    username: str
    password: str


class updateAdminInfoByUsernameModel(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    two_fa_status: Optional[bool] = None
    two_fa_key: Optional[str] = None

    def get_final_password(self) -> str:
        return self.newPassword if self.newPassword is not None else self.password


class userDelete(BaseModel):
    username: str


class newGroupModel(BaseModel):
    name: str
    traffic: float
    multi_login: int
    relative_expire_date: str


class updateGroupInfoByNameModel(BaseModel):
    name: Optional[str] = None
    traffic: Optional[float] = None
    multi_login: Optional[int] = None
    relative_expire_date: Optional[str] = None
