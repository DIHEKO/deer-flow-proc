from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from typing import Union
from src.server.secret_manager import (static_secret_manager, diheko_aws_secret_Manager)

class jwt_middleware:
    def __init__(self, app, secret_manager: Union[static_secret_manager, diheko_aws_secret_Manager], exempt_paths: list = []):
        self.app = app
        self.exempt_paths = exempt_paths  # paths that don't require auth
        self._secret_manager : Union[static_secret_manager, diheko_aws_secret_Manager]

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)

        if request.url.path in self.exempt_paths:
            await self.app(scope, receive, send)
            return

        auth_header = request.headers.get("Authorization")
        if auth_header is None or not auth_header.startswith("Bearer "):
            response = JSONResponse(status_code=401, content={"detail": "Missing or invalid token"})
            await response(scope, receive, send)
            return

        token = auth_header[len("Bearer "):]
        for secret in self._secret_manager.get_verification_secrets():
            try:
                payload = jwt.decode(token, secret, algorithms=["HS256"])
                await self.app(scope, receive, send)
                return
            except JWTError:
                pass

        response = JSONResponse(status_code=401, content={"detail": "Invalid token"})
        await response(scope, receive, send)
        
