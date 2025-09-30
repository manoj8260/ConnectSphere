from pydantic_settings import BaseSettings ,SettingsConfigDict
from pydantic import Field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR/".env"  
print('😊',BASE_DIR)
print('👆',ENV_PATH)
class Settings(BaseSettings):
    DATABASE_URL :str = Field(..., env='DATABASE_URL')
   
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        extra="ignore"
    )
    
    
Config = Settings()    

