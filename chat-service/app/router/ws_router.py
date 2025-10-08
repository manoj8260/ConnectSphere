import logging
from fastapi import APIRouter ,  WebSocket ,WebSocketDisconnect ,Query ,Depends
from app.servises.websocket_manager import WebSocketManager
from app.schema.message import ChatMessage,MessageType
from datetime import datetime
from app.core.dependency import get_current_user



logger = logging.getLogger(__name__)


wsrouter = APIRouter()
manager = WebSocketManager()

   
@wsrouter.websocket("/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str = Query(default="general"),
    token: str = Query(...)
):
    logger.info(f"WebSocket connection attempt - room: {room_id}")
    user_data = await get_current_user(token)
    # Accept the connection first
    try:
        await websocket.accept()
        logger.info("WebSocket accepted")
    except Exception as e:
        logger.error(f"Failed to accept WebSocket: {e}")
        return
    
    username =  user_data['user']['username']

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