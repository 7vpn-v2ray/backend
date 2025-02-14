from fastapi import HTTPException

class userNotFound(HTTPException):
    def __init__(self, route) -> None:
        self.status_code = 404
        self.detail = f"user not found in {route}"