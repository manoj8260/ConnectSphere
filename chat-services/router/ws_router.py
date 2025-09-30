import logging
from fastapi import APIRouter ,  WebSocket ,WebSocketDisconnect ,Query ,Depends
from chat.servises.websocket_manager import WebSocketManager
from chat.schema.message import ChatMessage,MessageType
from datetime import datetime
from auth.servises import AuthServices
from auth.utils.utils import verify_ws_token ,token_decode
from auth.database.connection import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession

logger = logging.getLogger(__name__)

user_servises = AuthServices()
wsrouter = APIRouter()
manager = WebSocketManager()

   
@wsrouter.websocket("/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str = Query(default="general"),
    token: str = Query(...)
):
    logger.info(f"WebSocket connection attempt - room: {room_id}")
    
    # Accept the connection first
    try:
        await websocket.accept()
        logger.info("WebSocket accepted")
    except Exception as e:
        logger.error(f"Failed to accept WebSocket: {e}")
        return
    
    # Now verify the token
    try:
        token_data = token_decode(token)
        logger.info(f"Token decoded successfully: {token_data.get('user', {}).get('email')}")
    except Exception as e:
        logger.error(f"Token decode failed: {e}")
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Continue with rest of the logic...

    # Get user from database
    try:
        async for session in get_session():
            user = await user_servises.get_user_by_email(token_data["user"]["email"],session)
            if not user:
               await websocket.close(code=1008, reason="User not found")
               return
            break # Exit the loop after getting the user
    except Exception as e:
        logger.error(f"Database error: {e}")
        await websocket.close(code=1011, reason="Server error")
        return

    username = user.username

    # Now connect to the manager
    await manager.connect(websocket, username, room_id)

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "message":
                chat_message = ChatMessage(
                    username=username,
                    message=data.get("message", ""),
                    message_type=MessageType.CHAT,
                    room_id=room_id,
                    timestamp=datetime.utcnow(),
                )
                await manager.broadcast_to_room(room_id, chat_message.dict())

            elif data.get("type") == "switch_room":
                new_room_id = data.get("room_id", "general")
                success = await manager.switch_user_room(username, new_room_id)
                if success:
                    room_id = new_room_id

    except WebSocketDisconnect:
        await manager.disconnect(username)
    except Exception as e:
        logger.error(f"WebSocket error for {username}: {e}")
        await manager.disconnect(username)