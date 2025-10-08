import uvicorn
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from app.router.ws_router import wsrouter 
from app.router.api_router import apirouter
from app.core.middleware import register_middleware
from app.database.connection import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    # filename='chat/app.log',      # The file where logs will be stored
    # filemode='a', 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

@asynccontextmanager
async def life_span(app:FastAPI):
    print("✅ Starting chat server...")
    
    # await init_db()
    yield
    
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
app.include_router(apirouter,prefix='/api',tags=["Api"])

# register middleware
register_middleware(app)


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











