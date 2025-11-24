from fastapi import Header
from app.utils.utils import token_decode
from app.utils.errors import InvalidOrExpireToken

async def get_current_user(authorization: str):
    if " " in authorization:
        token = authorization.split(" ")[1]
    else:
        token = authorization  
        
    payload = await token_decode(token)
    if not payload:
        raise InvalidOrExpireToken()
    return payload