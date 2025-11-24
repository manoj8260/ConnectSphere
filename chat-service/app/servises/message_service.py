from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi.exceptions import HTTPException
from sqlmodel import select 
from app.models.chat_room import Message
from app.schema.chat_room_schema import MessageType
from app.servises.user_snapshot_service import UserSnapshotService
from typing import List
import uuid

import logging

logger = logging.getLogger(__name__)


class MessageService:
    async def create_message(
        self, 
        session: AsyncSession, 
        room_id: uuid.UUID, 
        user_id: uuid.UUID, 
        message: str, 
        user_snapshot :  UserSnapshotService ,
        message_type: MessageType = MessageType.CHAT,
    ) -> Message: 
        try:
           
            if not isinstance(room_id, uuid.UUID) or not isinstance(user_id, uuid.UUID):
                raise ValueError("Invalid room_id or user_id: Must be UUID.")
            if len(message) > 5000:  # Example limit
                raise ValueError("Message too long (max 5000 characters).")
            snapshot = await user_snapshot.get_snapshot(session,user_id)
            sender_username = snapshot.username if snapshot else "Unknown"
            msg = Message(
                room_id=room_id, 
                user_id=user_id, 
                message=message, 
                sender_username=sender_username,
                message_type=message_type          
            )
            session.add(msg)
            await session.commit()
            await session.refresh(msg)
            return msg

        except ValueError as e:
            await session.rollback()
            logger.warning(f"Validation error in create_message: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error in create_message: {e}")
            raise HTTPException(status_code=500, detail="Failed to create message.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error in create_message: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")
     
    async def get_messages(
        self,
        session: AsyncSession, 
        room_id: uuid.UUID
    ) -> List[Message]:
        try:
            if not isinstance(room_id, uuid.UUID):
                raise ValueError("Invalid room_id: Must be UUID.")

            statement = select(Message).where(Message.room_id == room_id).order_by(Message.timestamp)
            result = await session.execute(statement)
            messages = result.scalars().all()  
            return messages

        except ValueError as e:
            logger.warning(f"Validation error in get_messages: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_messages: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch messages.")
        except Exception as e:
            logger.error(f"Unexpected error in get_messages: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")
        
   # Dependency to inject services 
def get_message_service() -> MessageService:
    return MessageService()