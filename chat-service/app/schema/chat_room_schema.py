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
    

class ChatMessage(BaseModel):
    room_name: str = Field(..., description="room_name of the room where message was sent")
    message: str = Field(..., description="The message content")
    message_type : MessageType = Field(default=MessageType.CHAT,description="Type of the message")
   

    

class UserInfo(BaseModel):
    username: str = Field(..., description="The username")
    current_room: Optional[str] = Field(None, description="Current room of the user") 
    connected_at: datetime = Field(default_factory=datetime.utcnow, description="Connection timestamp")
    is_online: bool = Field(default=True, description="Online status")   
    
          