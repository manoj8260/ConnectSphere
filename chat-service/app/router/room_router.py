from fastapi import FastAPI,APIRouter ,Depends,Header
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.database.connection import get_session
from app.schema.chat_room_schema import RoomInfo
from app.servises.room_service import RoomService , get_room_service
from app.core.dependency import get_current_user
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import uuid


roomrouter = APIRouter()


@roomrouter.get('/rooms')
async def rooms(session:AsyncSession=Depends(get_session),
                room_service:RoomService =Depends(get_room_service)):
    rooms = await room_service.get_all_rooms(session)
    return rooms
@roomrouter.get('/user_rooms')
async def user_rooms(session:AsyncSession=Depends(get_session),
                     authorization: str = Header(..., alias="Authorization"),
                     room_service:RoomService =Depends(get_room_service)):
    user_info = await get_current_user(authorization)
    user_id = uuid.UUID(user_info['user']['uid'])
    rooms = await room_service.get_rooms_user(session,user_id)
    return rooms
    


@roomrouter.post('/create_room')
async def create_room(room_info:RoomInfo,
                      session:AsyncSession=Depends(get_session), 
                      authorization: str = Header(...),
                      room_service:RoomService =Depends(get_room_service)):
    room_data = room_info.model_dump()
    user_data =await  get_current_user(authorization)
    creator_data = {
            "user_id": uuid.UUID(user_data['user']['uid']),
            "username": user_data['user']['username'],  
            "email": user_data['user']['email'],
            "name": user_data['user']['name'],
            "role": "admin",
            "is_active": True
        }
    
    room_data["creator_id"] = user_data['user']['uid']
    print(room_data,'🤔')
    create_room = await  room_service.create_room(room_data,session, creator_data)
    return create_room

@roomrouter.delete('/delete_room/{room_name}')
async def delete_room(room_name:str,
                      session:AsyncSession=Depends(get_session),
                      room_service:RoomService =Depends(get_room_service)):
        deleted_room = await room_service.delete_room(room_name,session)
        if deleted_room:
            return JSONResponse(
            content={"message": f"Room '{room_name}' deleted successfully."},
            status_code=200
           )
        raise HTTPException(
          status_code=404,
          detail=f"Room '{room_name}' not found."
         )
    
     
    