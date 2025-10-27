import uvicorn
import logging
from fastapi import FastAPI 
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi import Request
from app.router.ws_router import wsrouter 
from app.router.room_router import roomrouter
from app.router.message_router import messagerouter
from app.core.middleware import register_middleware
from app.utils.errors import ChatException
from app.database.connection import init_db
from app.servises.redis_manager import redis_manager
from app.servises.websocket_manager import manager  as ws_manager
from app.database.connection import get_session
from  app.core.config import Config
from typing import Dict ,Any

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    # filename='chat/app.log',      # The file where logs will be stored
    # filemode='a', 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
async def on_redis_message(room: str, payload: Dict[str, Any]):
    # Called whenever a message is received via Redis Pub/Sub
    await ws_manager.broadcast_to_room(room, payload)
    
@asynccontextmanager
async def life_span(app:FastAPI):
    print("✅ Starting chat server...")
    await redis_manager.connect(host=Config.REDIS_HOST, port=Config.REDIS_PORT, password=Config.password)
    await redis_manager.start_subscriber(on_redis_message)
    # await init_db()
    yield
    await redis_manager.disconnect()
    print("🛑 Stopping chat server...")


# Create FastAPI instance
version = "1.0.0"
app = FastAPI(
    title="WebSocket Chat Application",
    description="A real-time chat application using FastAPI and WebSockets",
    version=version,
    lifespan=life_span,
    docs_url="/docs",
    redoc_url="/redoc"
)

    
# Include WebSocket router
app.include_router(wsrouter, prefix='/ws', tags=["WebSocket"])
# app.include_router(apirouter,prefix='/api',tags=["Api"])
app.include_router(roomrouter,prefix='/room',tags=["Room"])
app.include_router(messagerouter,prefix='/message',tags=["Message"])

# register middleware
register_middleware(app)

#register error
@app.exception_handler(ChatException)
async def exception_handler(request : Request, exc :  ChatException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': exc.__class__.__name__ ,
            'message' : exc.message,
            'resulation' : exc.resulation
        }
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Status of the application
    """
    return {"status": "healthy", "message": "Chat application is running"}    
    

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=5002,
        reload=True,
        log_level="info"
    )












