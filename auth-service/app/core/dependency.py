from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.requests import Request
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import List
from app.core.utils import token_decode
from app.database.redis import is_token_blacklisted
from app.services.auth_service import AuthServices
from app.database.connection import get_session
from app.core.errors import InvalidOrExpireToken, UserNotFound
from functools import wraps

auth_servises = AuthServices()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
 
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        token = credentials.credentials
        token_data = token_decode(token)

        if not token_data:
            raise InvalidOrExpireToken()

        # Check blacklist
        jti = token_data["jti"]
        if await is_token_blacklisted(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNappORIZED,
                detail="Token has been revoked",
                headers={"WWW-appenticate": "Bearer"},
            )

        self.verify_token_type(token_data)
        return token_data

    def verify_token_type(self, token_data: dict):
        raise NotImplementedError("Please override in child class")


class AccessTokenBearer(TokenBearer):
    def verify_token_type(self, token_data: dict):
        if token_data and token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNappORIZED,
                detail={"message": "Access token required",
                        "hint": "You passed a refresh token"},
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_type(self, token_data: dict):
        if token_data and not token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNappORIZED,
                detail={"message": "Refresh token required",
                        "hint": "You passed an access token"},
            )

access_token =AccessTokenBearer()

async def get_current_user(
    token_data: dict = Depends(access_token),
    session: AsyncSession = Depends(get_session),
):
    email = token_data["user"]["email"]
    if not email:
        raise InvalidOrExpireToken()
    user = await auth_servises.get_user_by_email(email, session)
    if not user:
        raise UserNotFound()
    return user

async def login_required(user=Depends(get_current_user)):
    return user

def role_based_permission(allowed_roles :List[str]):
    def decorator(router_fun):
        @wraps(router_fun)
        async def role_checker(user= Depends(get_current_user),*args,**kwargs):
            if not user.role.lower() in [role.lower() for role in allowed_roles] :
                print(user.role)
                raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(allowed_roles)}"
               )          
            return await router_fun(*args,**kwargs)   
        return role_checker
    return decorator
    
    
            
    
        

