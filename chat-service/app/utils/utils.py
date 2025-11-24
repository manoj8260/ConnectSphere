from jose import jwt ,ExpiredSignatureError ,JWTError
from app.core.config import Config
from app.utils.errors import InvalidOrExpireToken
import logging

async def token_decode(token: str) -> dict:
    with open("keys/public.pem", "r") as f:
        public_key = f.read()
    try:
        user_data = jwt.decode(
            token=token,
            key=public_key,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return user_data
    except ExpiredSignatureError:
        logging.exception("Token expired")
        raise InvalidOrExpireToken()
     
    except JWTError:
        logging.exception("Invalid token")
        raise InvalidOrExpireToken()
       