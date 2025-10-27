import uuid
from typing import Optional,List
from datetime import datetime
from sqlmodel import SQLModel, Field, Column ,ForeignKey ,Relationship
from sqlalchemy.dialects import postgresql as pg
from app.schema.chat_room_schema import MessageType ,RoomType ,RoleType


from sqlalchemy import Enum , Text



class Room(SQLModel, table=True):
    __tablename__ = "rooms"

    rid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True, nullable=False)
    )
    room_name: str = Field(sa_column=Column(pg.VARCHAR(100), unique=True, index=True, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    room_type: RoomType = Field(sa_column=Column(pg.VARCHAR(20), default=RoomType.GROUP, nullable=False))
    is_active: bool = Field(default=True)

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False))
    
    # Just store the creator's user ID (no DB-level FK to auth-service)
    creator_id: uuid.UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), nullable=False, index=True))
    
    # Relationships within chat-service only
    messages: List["Message"] = Relationship(
        back_populates="room",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"}
    )
    participants: List["RoomParticipant"] = Relationship(
        back_populates="room",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"}
    )


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    mid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    )
    message: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    message_type: MessageType = Field(sa_column=Column(Enum(MessageType), nullable=False, default=MessageType.CHAT))
    timestamp: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False))
    
    # Just store the sender's user ID from auth-service
    user_id: uuid.UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), nullable=False, index=True))
    
    # FK only to local table rooms
    room_id: uuid.UUID = Field(
        sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("rooms.rid", ondelete="CASCADE"), nullable=False, index=True)
    )
    
    room: Optional[Room] = Relationship(back_populates="messages")

class RoomParticipant(SQLModel, table=True):
    __tablename__ = "room_participants"

    # Composite PK to prevent duplicates
    room_id: uuid.UUID = Field(
        sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("rooms.rid", ondelete="CASCADE"), primary_key=True, nullable=False, index=True)
    )
    user_id: uuid.UUID = Field(
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True, nullable=False, index=True)
    )
    role: RoleType = Field(
        sa_column=Column(pg.VARCHAR(20), nullable=False, default=RoleType.member)
    )
    joined_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False))

    room: Optional[Room] = Relationship(back_populates="participants")
