from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def register_middleware(app:FastAPI):
    
    app.add_middleware(
        middleware_class= CORSMiddleware,
        allow_origins  =[
            "http://127.0.0.1:3000",
            "http://localhost:3000",
        ],
        allow_methods = ['*'],
        allow_headers = ['*'] ,
        allow_credentials = True 
    )