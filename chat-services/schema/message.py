from pydantic import BaseModel ,Field
from datetime import datetime
from enum import Enum
from typing import List ,Optional


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

class ChatMessage(BaseModel):
    username :str =  Field(...,description="Username of the message sender")
    message: str = Field(..., description="The message content")
    message_type : MessageType = Field(default=MessageType.CHAT,description="Type of the message")
    room_id: str = Field(..., description="ID of the room where message was sent") # Use ID for consistency
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp") 
    
  
        
class RoomInfo(BaseModel):
    room_id: str = Field(..., description="Unique room identifier")
    users: List[str] = Field(default_factory=list, description="List of users in the room")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Room creation timestamp")
    message_count: int = Field(default=0, description="Number of messages sent in this room")
    
    
    

class UserInfo(BaseModel):
    username: str = Field(..., description="The username")
    current_room: Optional[str] = Field(None, description="Current room of the user") 
    connected_at: datetime = Field(default_factory=datetime.utcnow, description="Connection timestamp")
    is_online: bool = Field(default=True, description="Online status")   
    
          