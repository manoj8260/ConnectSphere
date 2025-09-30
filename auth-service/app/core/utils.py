import uuid
import logging
import hashlib
from passlib.context import CryptContext
from datetime import datetime ,timedelta
from app.core.config import Config
from app.core.errors import InvalidOrExpireToken ,RevokedToken
# jwt 
from jose import jwt ,JWTError ,ExpiredSignatureError
from app.database.redis import is_token_blacklisted

password_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

def _prehash(password: str) -> str:
    """
    Prepare a password to avoid bcrypt's 72-byte limit by 
    hashing it first with SHA-256. Always returns a fixed-length hex string.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def generate_password_hash(password :str)-> str:
    """Hash a password using bcrypt."""
    return password_context.hash(_prehash(password))

def verify_password(password:str,hash_password:str)->bool:
    """Verify a password against a stored hash."""
    return password_context.verify(_prehash(password),hash_password)
    
def create_token(user_data: dict ,expire_delta : timedelta | None =None ,refresh : bool =False ) ->str :
    payload = {}
    
    payload['user'] = user_data
    now = datetime.utcnow()
    payload['exp'] = now + (expire_delta or timedelta(seconds=Config.ACCESS_TOKEN_EXPIRE)) 
    payload['refresh'] = refresh
    payload['jti']  =  str(uuid.uuid4())
    payload['iat'] =  now
    
    token = jwt.encode(
        claims=payload,
        key=Config.JWT_SECRETKEY,
        algorithm=Config.JWT_ALGORITHM
    )
    return token


def token_decode(token: str) -> dict:
    try:
        user_data = jwt.decode(
            token=token,
            key=Config.JWT_SECRETKEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return user_data
    except ExpiredSignatureError:
        logging.exception("Token expired")
        raise InvalidOrExpireToken()
     
    except JWTError:
        logging.exception("Invalid token")
        raise InvalidOrExpireToken()
       

async def verify_ws_token(token: str):
    token_data = token_decode(token)
    jti = token_data["jti"]
    if await is_token_blacklisted(jti):
        raise RevokedToken()
    return token_data    