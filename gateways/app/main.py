from fastapi import FastAPI
from app.routes import auth_proxy, chat_proxy
import uvicorn
app = FastAPI(title="API Gateway")

app.include_router(auth_proxy.router)
app.include_router(chat_proxy.router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="info"
    )
