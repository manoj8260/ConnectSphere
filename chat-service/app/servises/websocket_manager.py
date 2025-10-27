import logging
from fastapi import WebSocket
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, Set[str]] = {}  # room -> usernames

    async def connect(self, websocket: WebSocket, username: str):
        print('hello🦢🦢🦢🦢🦢')
        self.active_connections[username] = websocket
        logger.info(f"WebSocket connected for user '{username}'")

    async def disconnect(self, username: str):
        if username in self.active_connections:
            del self.active_connections[username]
            logger.info(f"WebSocket disconnected for user '{username}'")

    def join_room(self, room: str, username: str):
        self.rooms.setdefault(room, set()).add(username)
        logger.info(f"User '{username}' joined room '{room}'")

    def leave_room(self, room: str, username: str):
        print('💖💖💖')
        if room in self.rooms:
            self.rooms[room].discard(username)
            if not self.rooms[room]:
                del self.rooms[room]
            logger.info(f"User '{username}' left room '{room}'")

    async def send_json_to_users(self, usernames: List[str], message: dict):
        disconnected_users = []
        for username in usernames:
            if websocket := self.active_connections.get(username):
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send message to '{username}': {e}. Marking for disconnect.")
                    disconnected_users.append(username)
        for username in disconnected_users:
            await self.disconnect(username)

    async def broadcast_to_room(self, room: str, message: dict):
        usernames = list(self.rooms.get(room, set()))
        if not usernames:
            return
        await self.send_json_to_users(usernames, message)

manager = WebSocketManager()