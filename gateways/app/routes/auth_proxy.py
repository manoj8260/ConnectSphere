from fastapi import APIRouter, Request
import httpx
from app.core.config import settings

router = APIRouter(prefix="/auth")

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.request(
            request.method,
            f"{settings.AUTH_SERVICE_URL}/{path}",
            params=request.query_params,
            json=await request.json() if request.method in ["POST", "PUT"] else None
        )
        return response.json()
