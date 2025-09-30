import uuid
from typing import Optional,List
from datetime import datetime
from sqlmodel import SQLModel, Field, Column ,ForeignKey ,Relationship
from sqlalchemy.dialects import postgresql as pg
from chat.schema.message import MessageType
from sqlalchemy import Enum



class Room(SQLModel, table=True):
    __tablename__ = "rooms"

    rid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True, nullable=False)
    )
    room_name: str = Field(sa_column=Column(pg.VARCHAR(100), unique=True, index=True, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False))
    # foreign key
    creator_id : uuid.UUID  = Field(sa_column=Column(pg.UUID,ForeignKey("users.uid",ondelete="CASCADE"),nullable=False))
    
    creator :"User"  = Relationship(back_populates="created_rooms")
    messages :List["Message"] = Relationship(back_populates ="room",sa_relationship_kwargs={"lazy": "selectin"} )


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    mid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    )
    message: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    message_type: MessageType = Field(sa_column=Column(Enum(MessageType), nullable=False, default=MessageType.CHAT))
    timestamp: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False))
    #foreign key
    user_id:uuid.UUID = Field(sa_column=Column(pg.UUID,ForeignKey("users.uid",ondelete="CASCADE"),nullable=False))
    room_id: uuid.UUID = Field(
    sa_column=Column(pg.UUID,ForeignKey("rooms.rid",ondelete="CASCADE"),nullable=False,index=True)
       
    )
    
    user: "User" = Relationship(back_populates="messages")
    room : Optional[Room] = Relationship(back_populates="messages")


