import redis.asyncio as aioredis
from app.core.config import Config
from datetime import datetime

token_blacklist = aioredis.from_url(
    url=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/0",
    encoding="utf-8",
    decode_responses=True    
)

async def blacklist_token(jti:str)-> None :
    ttl = Config.JTI_EXPIRY
    await token_blacklist.setex(f'blacklist:{jti}',ttl,'true')

async  def is_token_blacklisted(jti: str)->bool:
    return bool(await token_blacklist.exists(f"blacklist:{jti}")) 