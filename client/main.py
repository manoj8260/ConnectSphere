import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.requests import Request

@asynccontextmanager
async def life_span(app:FastAPI):
    print("✅ Starting client server...")
    
   
    yield
    
    print("🛑 Stopping client server...")
    
app = FastAPI(
    lifespan=life_span
)


# Mount static files (for CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(
    directory='templates'
)


    
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("landing_page.html", {"request": request})    
    
@app.get("/chat", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("chatpage.html", {"request": request})    
    
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8006,
        reload=True,
        log_level="info"
    )    
    
    
    
    
    
    
    
    
    
    