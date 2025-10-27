# from fastapi import APIRouter, Depends
# from typing import List ,Dict
# from app.schema.chat_room_schema import RoomInfo ,UserInfo
# from fastapi.exceptions import HTTPException
# from app.core.dependency import get_current_user
# from app.servises.websocket_manager import manager

# apirouter  = APIRouter()


# @apirouter.get("/messages")
# def get_messages(user_data=Depends(get_current_user)):
#     name = user_data['user']['name']
#     print(user_data)
#     return {"message": f"Hello user {name} , welcome to chat!"}

# # Room Information APIs
# @apirouter.get('/rooms', response_model=List[RoomInfo])
# async def get_all_rooms():
#     """
#     Get list of all active rooms with detailed information.
    
#     Returns:
#         List of RoomInfo objects containing room details
#     """
#     return manager.get_all_rooms()


# @apirouter.get('/rooms/{room_id}', response_model=RoomInfo)
# async def get_room_info(room_id: str):
#     """
#     Get detailed information about a specific room.
    
#     Args:
#         room_id: The room ID to get info for
        
#     Returns:
#         RoomInfo object with room details
        
#     Raises:
#         HTTPException: If room not found
#     """
#     room_info = manager.get_room_info(room_id)
#     if not room_info:
#         raise HTTPException(status_code=404, detail=f"Room '{room_id}' not found")
#     return room_info


# @apirouter.get('/rooms/{room_id}/users', response_model=List[str])
# async def get_room_users(room_id: str):
#     """
#     Get list of users in a specific room.
    
#     Args:
#         room_id: The room ID
        
#     Returns:
#         List of usernames in the room
#     """
#     users = manager.get_room_users(room_id)
#     return users


# # User Information APIs
# @apirouter.get('/users', response_model=List[UserInfo])
# async def get_all_users():
#     """
#     Get list of all users (online and offline).
    
#     Returns:
#         List of UserInfo objects
#     """
#     return list(manager.users.values())


# @apirouter.get('/users/online', response_model=List[UserInfo])
# async def get_online_users():
#     """
#     Get list of all currently online users.
    
#     Returns:
#         List of UserInfo objects for online users
#     """
#     return manager.get_online_users()


# @apirouter.get('/users/{username}', response_model=UserInfo)
# async def get_user_info(username: str):
#     """
#     Get detailed information about a specific user.
    
#     Args:
#         username: The username to get info for
        
#     Returns:
#         UserInfo object with user details
        
#     Raises:
#         HTTPException: If user not found
#     """
#     user_info = manager.get_user_info(username)
#     if not user_info:
#         raise HTTPException(status_code=404, detail=f"User '{username}' not found")
#     return user_info


# # Statistics APIs
# @apirouter.get('/stats/rooms', response_model=Dict[str, int])
# async def get_room_user_counts():
#     """
#     Get user count for each room.
    
#     Returns:
#         Dictionary mapping room_id to user count
#     """
#     return manager.get_user_count_by_room()


# @apirouter.get('/stats/messages')
# async def get_message_stats():
#     """
#     Get message statistics across all rooms.
    
#     Returns:
#         Dictionary with message statistics
#     """
#     total_messages = manager.get_total_message_count()
#     room_stats = {}
    
#     for room_id, room_info in manager.rooms.items():
#         room_stats[room_id] = {
#             "message_count": room_info.message_count,
#             "user_count": len(room_info.users),
#             "created_at": room_info.created_at.isoformat()
#         }
    
#     return {
#         "total_messages": total_messages,
#         "total_rooms": len(manager.rooms),
#         "total_online_users": len(manager.get_online_users()),
#         "room_statistics": room_stats
#     }


# # Room Management APIs
# @apirouter.post('/users/{username}/switch-room')
# async def switch_user_room(username: str, room_id: str):
#     """
#     Switch a user to a different room.
    
#     Args:
#         username: The username to switch
#         room_id: The new room ID to join
        
#     Returns:
#         Success message
        
#     Raises:
#         HTTPException: If user not found or operation fails
#     """
#     user_info = manager.get_user_info(username)
#     if not user_info:
#         raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    
#     if not user_info.is_online:
#         raise HTTPException(status_code=400, detail=f"User '{username}' is not online")
    
#     success = await manager.switch_user_room(username, room_id)
#     if not success:
#         raise HTTPException(status_code=500, detail="Failed to switch room")
    
#     return {"message": f"User '{username}' switched to room '{room_id}'"}


# @apirouter.delete('/rooms/{room_id}')
# async def delete_empty_room(room_id: str):
#     """
#     Delete a room if it's empty.
    
#     Args:
#         room_id: The room ID to delete
        
#     Returns:
#         Success message
        
#     Raises:
#         HTTPException: If room not found or not empty
#     """
#     room_info = manager.get_room_info(room_id)
#     if not room_info:
#         raise HTTPException(status_code=404, detail=f"Room '{room_id}' not found")
    
#     if room_info.users:
#         raise HTTPException(
#             status_code=400, 
#             detail=f"Room '{room_id}' is not empty. It has {len(room_info.users)} users."
#         )
    
#     del manager.rooms[room_id]
#     return {"message": f"Room '{room_id}' deleted successfully"}