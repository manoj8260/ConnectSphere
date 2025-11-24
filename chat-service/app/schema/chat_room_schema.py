from pydantic import BaseModel ,Field
from datetime import datetime
from enum import Enum
from typing import List ,Optional
import uuid

class RoomType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"
    PUBLIC = "public"
class RoleType(str, Enum):
    admin = "admin"
    member = "member"
    moderator = "moderator"
    
class MessageType(str,Enum):
    """
    Enumeration of different message types in the chat system.
    """
    CHAT = "chat"
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    ROOM_UPDATE = "room_update"
    ERROR = "error"
    SYSTEM = "system"
    
class RoomInfo(BaseModel):
    room_name: str = Field(..., description="Unique room identifier")
    description: Optional[str] = None
    room_type: RoomType = RoomType.GROUP
    

# class ChatMessage(BaseModel): 
#     room_name: str 
#     message: str 
#     message_type : MessageType 
#     message_id :uuid.UUID
    
   

    

class UserInfo(BaseModel):
    username: str = Field(..., description="The username")
    current_room: Optional[str] = Field(None, description="Current room of the user") 
    connected_at: datetime = Field(default_factory=datetime.utcnow, description="Connection timestamp")
    is_online: bool = Field(default=True, description="Online status")   
    

# --- Base Schema ---
class MessageBase(BaseModel):
    message: str = Field(..., example="Hello everyone!")
    message_type: MessageType = Field(default=MessageType.CHAT, example="chat")


# --- Create Schema ---
class MessageCreate(MessageBase):
    room_name: str
    


# --- Read Schema ---
class MessageRead(MessageBase):
    mid: uuid.UUID
    timestamp: datetime
    user_id: uuid.UUID
    room_id: uuid.UUID
    # username: Optional[str] = Field(None, description="Optional username for display (from auth service)")
    sender_username :str 
    
    class Config:
        orm_mode = True
