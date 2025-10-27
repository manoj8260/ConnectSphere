from pydantic_settings import BaseSettings ,SettingsConfigDict
from pydantic import Field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR/".env"  
print('😊',BASE_DIR)
print('👆',ENV_PATH)
class Settings(BaseSettings):
    DATABASE_URL :str = Field(..., env='DATABASE_URL')
    JWT_ALGORITHM :str 
    
    REDIS_HOST : str = Field(default='localhost')
    REDIS_PORT :int =  Field(default=6379)
    password :str  
   
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        extra="ignore"
    )
    
    
Config = Settings()    

