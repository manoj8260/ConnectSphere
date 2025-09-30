import logging
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from typing import Dict, List ,Optional
from chat.schema.message import ChatMessage, MessageType , UserInfo ,RoomInfo
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections and handles message broadcasting.

    This class maintains active connections, handles user join/leave events,
    and broadcasts messages to connected clients.
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.users: Dict[str, UserInfo] = {}   # username -> UserInfo
        self.rooms: Dict[str, RoomInfo] = {}   # room_id -> RoomInfo

    async def connect(self, websocket: WebSocket, username: str, room_id: str = "general"):
        """
        Accept a new WebSocket connection and add user to room.
        
        Args:
            websocket: The WebSocket connection
            username: The username of the connecting user
            room_id: The room ID to join (default: "general")
        """
        
        if username in self.users:
            old_room = self.users[username].current_room
            if old_room  and  old_room != room_id  :
                 await self._remove_user_from_room(username, old_room)
            
            self.users[username].current_room  =room_id        
            self.users[username].connected_at  =datetime.utcnow()      
            self.users[username].is_online  =True  
        else:       
            # Create new user
            self.users[username] = UserInfo(
            username=username,
            current_room=room_id,
            connected_at=datetime.utcnow(),
            is_online=True
            )
        # Add connection
        self.active_connections[username] =  websocket
        
        # add user to room
        await self._add_user_to_room(username,room_id)
        
        # broadcast the message
        join_message = ChatMessage(
            username=username,
            message=f"{username} joined the room",
            message_type=MessageType.USER_JOIN,
            room_id=room_id,
            timestamp=datetime.utcnow()
        )
        await self._broadcast_to_room_safe(room_id,join_message.dict())
        logger.info(f"User {username} connected to room {room_id}")
        print(f"websocket user : {[ k for k ,v in self.active_connections.items()]}")
        print(self.users)
        
    async def disconnect(self, username: str):
        """
        Remove a user's WebSocket connection and update their status.
        
        Args:
            username: The username to disconnect
        """  
        if username in self.users:
            user = self.users[username]
            user.is_online =  False
            room_id = user.current_room
            
            #  Remove from room and connections
            if room_id :
                 await  self._remove_user_from_room(username,room_id)
            if   username in self.active_connections:
                del self.active_connections[username]  
            leave_message = ChatMessage(
                    username=username,
                    message=f"{username} left the room",
                    message_type=MessageType.USER_LEAVE,
                    room_id=room_id,
                    timestamp=datetime.utcnow()
                )   
            await self._broadcast_to_room_safe(room_id,leave_message.dict())  
        logger.info(f"User {username} disconnected from room {room_id}")      
        
    async def _add_user_to_room(self,username : str, room_id: str):
        """Add a user to a room, creating the room if it doesn't exist."""
        if room_id not in self.rooms :
            self.rooms[room_id] = RoomInfo(
                room_id=room_id,
                users=[username],
                created_at=datetime.utcnow()
            )
        room = self.rooms[room_id]
        if username not in room.users:
            room.users.append(username) 
        logger.info('user')
     
    async def _remove_user_from_room(self,username : str, room_id: str):
        """Remove a user from a room, cleaning up empty rooms."""
        if room_id in self.rooms:
            room = self.rooms[room_id]
            if username in room.users:
                room.users.remove(username)
            
            # Clean up empty rooms
            if not room.users:
                del self.rooms[room_id]
                logger.info(f"Room {room_id} deleted (no users left)")    
              
    
    async def send_personal_message(self, username: str, message:dict):
        """
        Send a message to a specific user.
        
        Args:
            username: The target username
            message: The message to send
        """
        if username in self.active_connections and  username in self.users:
            if self.users[username].is_online :
              websocket = self.active_connections[username] 
              try :
                await websocket.send_json(jsonable_encoder(message))
                logger.info(f"Message successfully sent to {username}")
              except  Exception as e :
                await self._handle_connection_error(username)
                logger.error(f"Error sending message to {username}: {str(e)}")   
            else:
              logger.warning(f"User {username} is offline, message not sent")
                       
    
    async def broadcast_to_room(self,room_id:str,message:dict):
        """Broadcast a message to all users in a room and increment message count."""
        if room_id in self.rooms and message.get("message_type") == MessageType.CHAT:
            self.rooms[room_id].message_count +=1
            logger.info(self.rooms[room_id].message_count)
            
        await   self._broadcast_to_room_safe(room_id,message)
        
            
        
    async def _broadcast_to_room_safe(self, room_id: str, message:dict,exclude_user: str = None):
        """Safely broadcast a message to all users in a room."""
        if room_id not in self.rooms:
            logger.warning(f"Attempted to broadcast to non-existent room '{room_id}'")
            return
        room=self.rooms[room_id]
        failed_users = []
        
        for username in room.users:
             # Skip excluded user
            if exclude_user and exclude_user ==  username:
                continue
             # Only send to online users with active connections
            if (username in self.users and
                 self.users[username].is_online == True and
                 username in self.active_connections) :
                try:
                    websocket =  self.active_connections[username]
                    await websocket.send_json(jsonable_encoder(message))
                except Exception as e :
                    logger.error(f"Error sending message to '{username}': {str(e)}")
                    failed_users.append(username)    
        for username in  failed_users:
            await self._handle_connection_error(username)        
        
    
    async def switch_user_room(self, username: str, new_room_id: str) -> bool:
        """
        Switch a user from their current room to a new room.
        
        Args:
            username: The username to switch
            new_room_id: The new room to join
            
        Returns:
            bool: True if successful, False otherwise
        """
        if username not in self.users or not self.users[username].is_online:
            return False
        
        user = self.users[username]
        old_room = user.current_room
        
        # Remove from old room
        if old_room:
            await self._remove_user_from_room(username, old_room)
            
            # Broadcast leave message to old room
            leave_message = ChatMessage(
                username=username,
                message=f"{username} left the room",
                message_type=MessageType.USER_LEAVE,
                room_id=old_room,
                timestamp=datetime.utcnow()
            )
            await self._broadcast_to_room_safe(old_room, leave_message.dict())
        
        # Add to new room
        user.current_room = new_room_id
        await self._add_user_to_room(username, new_room_id)
        
        # Broadcast join message to new room
        join_message = ChatMessage(
            username=username,
            message=f"{username} joined the room",
            message_type=MessageType.USER_JOIN,
            room_id=new_room_id,
            timestamp=datetime.utcnow()
        )
        await self._broadcast_to_room_safe(new_room_id, join_message.dict(), exclude_user=username)
        
        logger.info(f"User {username} switched from {old_room} to {new_room_id}")
        return True
    
    async def _handle_connection_error(self, username: str):
        if username in self.users:
            user = self.users[username]
            room_id = user.current_room
            
            user.is_online = False
            if room_id :
                await self._remove_user_from_room(username,room_id)  
             # Remove from active connections
            if username in self.active_connections:
                del self.active_connections[username] 
                         
    def get_room_info(self, room_id: str) -> Optional[RoomInfo]:
        """Get detailed room information."""
        return self.rooms.get(room_id)
    
    def get_user_info(self, username: str) -> Optional[UserInfo]:
        """Get detailed user information."""
        return self.users.get(username)
    
    def get_all_rooms(self) -> List[RoomInfo]:
        """Get list of all active rooms with details."""
        return list(self.rooms.values())
    
    def get_online_users(self) -> List[UserInfo]:
        """Get list of all online users."""
        return [user for user in self.users.values() if user.is_online]
    
    def get_room_users(self, room_id: str) -> List[str]:
        """Get list of usernames in a room."""
        if room_id in self.rooms:
            return self.rooms[room_id].users.copy()
        return []
    
    def get_user_count_by_room(self) -> Dict[str, int]:
        """Get user count for each room."""
        return {room_id: len(room.users) for room_id, room in self.rooms.items()}
    
    def get_total_message_count(self) -> int:
        """Get total messages across all rooms."""
        return sum(room.message_count for room in self.rooms.values())