from fastapi import APIRouter, WebSocket, Query
from app.core.config import settings
from app.utils.token_utils import verify_jwt_token
from fastapi import WebSocket
import asyncio
import logging

router = APIRouter(prefix="/chat")
logger = logging.getLogger(__name__)

@router.websocket("/ws")
async def chat_proxy(websocket: WebSocket, token: str = Query(...), room_id: str = Query(default="general")):
    # Step 1. Verify JWT
    try:
        user_data = verify_jwt_token(token, settings.JWT_SECRET)
        username = user_data["user"]["username"]
        logger.info(f"✅ Token verified for user: {username}")
    except Exception as e:
        await websocket.close(code=4001, reason="Unauthorized WebSocket connection")
        logger.error(f"❌ Token verification failed: {e}")
        return

    # Step 2. Connect to ChatService WebSocket
    chat_ws_url = f"ws://chat-service:8001/chat?token={token}&room_id={room_id}"
    async with websocket.connect(chat_ws_url) as chat_ws:
        await websocket.accept()

        async def client_to_service():
            async for message in websocket.iter_text():
                await chat_ws.send(message)

        async def service_to_client():
            async for message in chat_ws:
                await websocket.send_text(message)

        await asyncio.gather(client_to_service(), service_to_client())
