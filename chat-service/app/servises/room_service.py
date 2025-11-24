from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select ,delete 
from fastapi import Depends
from app.models.chat_room import Room , RoomParticipant
from app.schema.chat_room_schema import RoomInfo ,RoleType
from app.utils.errors import (RoomAleradyExists , RoomNotFound)
from sqlalchemy.exc import SQLAlchemyError
from fastapi.exceptions import HTTPException
from app.servises.user_snapshot_service import  UserSnapshotService ,get_user_snapshot_service
from typing import Optional
import uuid

import logging

logger = logging.getLogger(__name__)

class RoomService:
    def __init__(self, user_snapshot_service: UserSnapshotService):
        self.user_snapshot_service = user_snapshot_service

    async def get_all_rooms(self,session:AsyncSession) -> list[Room]:
        try:
            statement = select(Room)
            result = await session.execute(statement)
            rooms = result.scalars().all()

            if not rooms:
                logger.info("No rooms found in database.")
                return []  # Empty list instead of raising error (better UX)

            return rooms

        except SQLAlchemyError as e:
            logger.error(f"Database error in get_all_rooms: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch rooms due to a database error."
            )
        except Exception as e:
            logger.error(f"Unexpected error in get_all_rooms: {e}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while fetching rooms."
            )
    async def get_rooms_user(self,session:AsyncSession,uid:uuid.UUID):
        query = (
        select(Room)
        .join(RoomParticipant, Room.rid == RoomParticipant.room_id)
        .where(RoomParticipant.user_id == uid)
        ) 
        result = await session.execute(query)
        rooms = result.scalars().all()
        return rooms
        
                

    async def _room_exists_by_id(self,rid:str,session:AsyncSession)-> Optional[Room]:
        """Fetch a room by its UUID."""
        try:
            room_id = uuid.UUID(rid)
        except ValueError:
            return None 
        statement = select(Room).where(Room.rid==room_id)
        
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def _room_exists_by_name(self,room_name:str,session:AsyncSession)-> Optional[Room]:
        """Fetch a room by its unique name."""
        statement = select(Room).where(Room.room_name==room_name)
        
        result =  await session.execute(statement)
        return result.scalar_one_or_none()
    
    async def _participant_exists(
        self,
        room_id: uuid.UUID,
        user_id: uuid.UUID,
        session: AsyncSession
    ) -> bool:
        stmt = select(RoomParticipant).where(
            RoomParticipant.room_id == room_id,
            RoomParticipant.user_id == user_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None
   
    async def create_or_join_room(
        self,
        room_data: dict,
        user_data: dict,
        session: AsyncSession
    ) -> Room:
        """
        If the room exists, user joins it.
        If it doesn't, user creates it.
        """
        # 1️⃣ Check if room already exists

        existing_room = await self._room_exists_by_name(room_data["room_name"], session)

        # Get or create user snapshot
        snapshot = await self.user_snapshot_service.upsert_snapshot(session, user_data)

        if existing_room:
            # 2️⃣ If room exists → add user as participant if not already there
            already_participant = await self._participant_exists(
                existing_room.rid, snapshot.user_id, session
            )

            if already_participant:
                logger.info(f"User {snapshot.user_id} already joined room '{existing_room.room_name}'.")
                return existing_room

            participant = RoomParticipant(
                room_id=existing_room.rid,
                user_id=snapshot.user_id,
                role=RoleType.member
            )
            session.add(participant)
            await session.commit()
            await session.refresh(existing_room)
            logger.info(f"User {snapshot.user_id} joined existing room '{existing_room.room_name}'.")
            return existing_room

        else:
            # 3️⃣ If room doesn’t exist → create new one
            new_room = Room(
                room_name=room_data["room_name"],
                description=room_data.get("description", ""),
                room_type=room_data.get("room_type", "public"),
                creator_id=snapshot.user_id
            )
            session.add(new_room)
            await session.flush()  # Get room ID

            # Creator becomes admin
            participant = RoomParticipant(
                room_id=new_room.rid,
                user_id=snapshot.user_id,
                role=RoleType.admin
            )
            session.add(participant)
            await session.commit()
            await session.refresh(new_room)
            logger.info(f"Room '{new_room.room_name}' created by {snapshot.user_id}")
            return new_room

    async def delete_room(self,room_name:str,session:AsyncSession)->bool:
        room = await self._room_exists_by_name(room_name,session)
        
        if not room  :
             return False
         # Delete also all participants (cascading )
        await session.execute(
            delete(RoomParticipant).where(RoomParticipant.room_id == room.rid)
        ) 
        await session.delete(room)
        await  session.commit()  
        logger.info(f"Room '{room_name}' and its participants deleted successfully.")
        return True
       
    
    async def add_participant(self,
                              session:AsyncSession,
                              room_id: uuid.UUID, 
                              user_id: uuid.UUID, 
                              role: RoleType = RoleType.member)-> Optional[RoomParticipant]:
        room =  await self._room_exists_by_id(room_id,session)
        if room is   None :
             raise RoomNotFound()
         # Check if participant already exists (optional)
        if await self._participant_exists(room_id, user_id, session):
            logger.warning(f"User {user_id} already in room {room_id}")
            return None 
        participant = RoomParticipant(room_id=room.rid, user_id=user_id, role=role)
        session.add(participant)
        await session.commit()
        await session.refresh(participant)
        return participant
       
    
    async def remove_participant(self, 
                                 session: AsyncSession, 
                                 room_id: uuid.UUID,
                                 user_id: uuid.UUID) -> bool:
        stmt = select(RoomParticipant).where(
        RoomParticipant.room_id == room_id,
        RoomParticipant.user_id == user_id
    )
        result = await session.execute(stmt)
        participant = result.scalar_one_or_none()
            
        if participant:
            await session.delete(participant)
            await session.commit()
            return True
        logger.warning(f"User {user_id} already in room {room_id}")
        return False
    
    async def update_role(
                         self,
                         session: AsyncSession, 
                         room_id: uuid.UUID, 
                         user_id: uuid.UUID,
                         new_role: RoleType) -> Optional[RoomParticipant]:
        statement = select(RoomParticipant).where(
                RoomParticipant.room_id == room_id,
                RoomParticipant.user_id == user_id
            )
        result =  await session.execute(statement)
        
        participant = result.scalar_one_or_none()
        if participant :
            participant.role =  new_role
            await session.commit()
            await session.refresh(participant)
            return participant
        return  None
    
    async def check_user_in_room(self,
                                room_id: uuid.UUID, 
                                user_id: uuid.UUID,
                                session:AsyncSession) -> bool:
        statement = select(RoomParticipant).where(
                RoomParticipant.room_id == room_id,
                RoomParticipant.user_id == user_id
            )
        participant_result = await session.execute(statement)
        participant = participant_result.scalar_one_or_none()
        if not participant:
                logger.warning(f"User {user_id} tried to send message to room {room_id} without being a participant.")
                # raise PermissionError(f"You are not a participant of this room {room_id}.")
                return False
        return True    

            

def get_room_service(snapshot_service:UserSnapshotService = Depends(get_user_snapshot_service)) -> RoomService:
    return RoomService(snapshot_service)     
        
            
            
        
                
