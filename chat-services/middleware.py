from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def register_middleware(app:FastAPI):
    
    app.add_middleware(
        middleware_class= CORSMiddleware,
        allow_origins  =['*'],
        allow_methods = ['*'],
        allow_headers = ['*'] ,
        allow_credentials = True 
    )