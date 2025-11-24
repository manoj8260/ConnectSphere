# app/api/wsrouter.py
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from app.servises.websocket_manager import manager  # use the singleton, do NOT re-instantiate
from app.servises.redis_manager import redis_manager
from app.core.dependency import get_current_user
from app.servises.message_service import get_message_service, MessageService
from app.servises.room_service import get_room_service, RoomService
from app.servises.user_snapshot_service import get_user_snapshot_service , UserSnapshotService
from app.database.connection import get_session
import uuid

logger = logging.getLogger(__name__)
wsrouter = APIRouter()

@wsrouter.websocket("/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    room_name: str ,
    token: str = Query(...),
    message_service: MessageService = Depends(get_message_service),
    room_service: RoomService = Depends(get_room_service),
    user_snapshot_service : UserSnapshotService = Depends(get_user_snapshot_service)
):
    try:
        await websocket.accept()
        logger.info("WebSocket accepted")
    except Exception as e:
        logger.error(f"Failed to accept WebSocket: {e}")
        return   
    logger.info(f"WebSocket connection attempt - room: {room_name}")
    user_data = await get_current_user(token)
    username = user_data["user"]["username"]
    user_id = user_data["user"]["uid"]

    await manager.connect(websocket, username)

    async for session in get_session():
       room = await room_service._room_exists_by_name(room_name, session)
       if not room:
         await websocket.send_json({"error": f"Room '{room_name}' not found."})
         await websocket.close()
         return  # or break

    # Join the room locally so this instance can broadcast to this user
    manager.join_room(room_name, username)

    try:
        while True:
            data = await websocket.receive_json() 
            # Persist the message
            new_message = await message_service.create_message(
                session=session, room_id=room.rid, user_id=uuid.UUID(user_id),user_snapshot= user_snapshot_service, message=data.get('message')
            )

            # Publish to Redis so all instances relay it to that room
            message_to_publish = {
                "username": username,
                "message": new_message.message,
                "timestamp": new_message.timestamp.isoformat(),
            }
            await redis_manager.publish(room_name, message_to_publish)

    except WebSocketDisconnect:
        manager.leave_room(room_name, username)
        await manager.disconnect(username)
        await websocket.close()
    except Exception as e:
        logger.error(f"WebSocket error for {username}: {e}")
        manager.leave_room(room_name, username)
        await manager.disconnect(username)
        await websocket.close()
        
        