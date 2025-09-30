import uvicorn
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.database.connection import init_db
from app.routers.auth_router import auth_router
from app.routers.user_router import user_router
from app.core.errors import AuthOrUserException
from app.core.middleware import register_middleware


@asynccontextmanager
async def life_span(app:FastAPI):
    print("✅ Starting auth server...")
    
    # await init_db()
    yield
    
    print("🛑 Stopping auth server...")

version ='v1'
app =FastAPI(
    title='Messenger-Auth',
    description='None',
    version=version,
    lifespan=life_span 
)

# register middleware
register_middleware(app)

@app.exception_handler(AuthOrUserException)
async def exception_handler(request : Request, exc :  AuthOrUserException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': exc.__class__.__name__ ,
            'message' : exc.message,
            'resulation' : exc.resulation
        }
    )


app.include_router(auth_router,prefix=f'/api/{version}/auth' , tags=['Auth'])
app.include_router(user_router,prefix=f'/api/{version}/user' , tags=['User'])

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="info"
    )






