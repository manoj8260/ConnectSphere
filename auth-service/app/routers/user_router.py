from fastapi import APIRouter ,Depends
from fastapi.responses import JSONResponse 
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.database.connection import get_session
from app.services.user_service import UserServise
from app.core.dependency import role_based_permission ,login_required
from typing import List
from app.core.errors import UserNotFound
from app.schemas.user_schema import UserRead ,UserUpdate



user_router = APIRouter()
user_servise = UserServise()


@user_router.get("/users",response_model=List[UserRead])
@role_based_permission(['admin'])
async def get_users(session:AsyncSession = Depends(get_session),user= Depends(login_required)):
    
    users = await user_servise.get_users(session)
    return users

@user_router.get("/{user_uid}")
async def get_user(user_uid:str,session:AsyncSession= Depends(get_session)):
    
    user = await user_servise.get_user_by_uid(user_uid,session)
    if user:
        return user
    else:
      return JSONResponse(
          content={
              "message":"user not found or wrong uid"
          },
          status_code=400
      )

@user_router.patch("/{user_uid}")        
async def update_user(user_uid:str,user_data:UserUpdate,session:AsyncSession=Depends(get_session),user=Depends(login_required)):
    user_dict = user_data.model_dump()
    updated_user =await user_servise.update_user(user_uid,user_dict,session)
    if not updated_user:
        raise UserNotFound()
    return updated_user
    
  
    
    