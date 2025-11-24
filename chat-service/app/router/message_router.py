from fastapi import FastAPI,APIRouter ,Depends,Header
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.database.connection import get_session
from app.schema.chat_room_schema import     MessageRead ,MessageCreate
from app.servises.message_service import MessageService ,get_message_service
from app.servises.room_service import RoomService ,get_room_service
from app.servises.user_snapshot_service import get_user_snapshot_service ,UserSnapshotService
from app.core.dependency import get_current_user
from app.models.chat_room import Message
from fastapi.exceptions import HTTPException
from fastapi import status
from typing import List
import uuid

import logging

logger = logging.getLogger(__name__)

messagerouter = APIRouter()

@messagerouter.post("/send_msg", response_model=Message, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_info: MessageCreate,
    session: AsyncSession = Depends(get_session),
    authorization: str = Header(..., alias="Authorization"),
    message_service: MessageService = Depends(get_message_service),
    room_service: RoomService = Depends(get_room_service),
    user_snapshot_service : UserSnapshotService = Depends(get_user_snapshot_service)
):
    try:
        # Validate input
        if not message_info.message or not message_info.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message content cannot be empty."
            )

        # Get room (with error handling)
        room_info = await room_service._room_exists_by_name(message_info.room_name, session)
        if not room_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room '{message_info.room_name}' not found."
            )
        room_id = room_info.rid

        # Authenticate user
        user_info = await get_current_user(authorization)
        user_id = uuid.UUID(user_info['user']['uid'])

        # Check if user is in room (placeholder - implement in RoomService)
        if not await room_service.check_user_in_room(room_id, user_id, session):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to send messages in this room."
            )
        # print('🦢',message)
        # Create message
        new_message = await message_service.create_message(
            session, room_id, user_id, message_info.message.strip(), user_snapshot=user_snapshot_service, message_type= message_info.message_type
        )

        logger.info(f"Message sent successfully: ID={new_message.mid}, Room={room_id}, User={user_id}")
        return new_message

    except HTTPException:
        # Re-raise FastAPI exceptions
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Database error while sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message due to a database error. Please try again."
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error while sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )
        
@messagerouter.get('/messages/{room_name}',response_model=List[MessageRead])
async def get_messages(room_name:str,
                       session:AsyncSession=Depends(get_session),
                       room_service:RoomService=Depends(get_room_service),
                       message_service:MessageService=Depends(get_message_service),):
        room_info = await room_service._room_exists_by_name(room_name, session)
        if not room_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room '{room_name}' not found."
            )
        room_id = room_info.rid
        messages = await message_service.get_messages(session,room_id)
        return  messages
        