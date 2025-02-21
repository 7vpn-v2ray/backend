from fastapi import HTTPException

class userNotFound(HTTPException):
    def __init__(self, route) -> None:
        self.status_code = 404
        self.detail = f"user not found in {route}"


class adminNotFound(HTTPException):
    def __init__(self, route) -> None:
        self.status_code = 404
        self.detail = f"admin not found in {route}"


class userExisted(HTTPException):
    def __init__(self, route) -> None:
        self.status_code = 400
        self.detail = f"user already existed in {route}"

class userOrPasswordIncorrect(HTTPException):
    def __init__(self, route) -> None:
        self.status_code = 400
        self.detail = f"uer or password is incorrect in {route}"

class groupExisted(HTTPException):
    def __init__(self, route) -> None:
        self.status_code = 400
        self.detail = f"group already existed in {route}"


class groupNotFound(HTTPException):
    def __init__(self, route) -> None:
        self.status_code = 400
        self.detail = f"group not found in {route}"
