from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Header, status, HTTPException, Request

from schema.jwt import JWTPayload, JWTResponsePayload
from settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


class JWTHandler:
    @staticmethod
    def generate(username: str, client_ip: str, exp_timestamp: int or None = None) -> JWTResponsePayload:
        expire_time = ACCESS_TOKEN_EXPIRE_MINUTES
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=expire_time)

        to_encode = {
            "exp": exp_timestamp if exp_timestamp else int(expires_delta.timestamp()),
            "username": username,
            # "ip": client_ip,
        }
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
        return JWTResponsePayload(access=encoded_jwt)

    @staticmethod
    def verify_token(request: Request, auth_token: Annotated[str, Header()]) -> JWTPayload:
        if not auth_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Auth header not found.",
            )
        try:
            token_data = jwt.decode(auth_token, SECRET_KEY, algorithms=[ALGORITHM])
            if datetime.fromtimestamp(token_data["exp"]) < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # token_ip = token_data.get("ip")
            #
            # client_ip = request.client.host
            #
            # if token_ip != client_ip:
            #     raise HTTPException(
            #         status_code=status.HTTP_403_FORBIDDEN,
            #         detail="Invalid IP address",
            #     )

        except jwt.exceptions.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return JWTPayload(**token_data)
