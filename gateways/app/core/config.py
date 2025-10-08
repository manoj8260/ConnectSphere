from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AUTH_SERVICE_URL: str = "http://localhost:5001"
    CHAT_SERVICE_URL: str = "http://localhost:5002"
    JWT_SECRET: str = "ndrijr5809vn_ffvn3211"

settings = Settings()
