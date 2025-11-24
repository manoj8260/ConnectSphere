import uuid
from fastapi import Depends
from  sqlalchemy.ext.asyncio.session import AsyncSession
from  app.database.connection import  get_session
from  app.models.user_model import User
from sqlmodel import select ,desc
# from app.events.publisher import event_publisher

class UserServise:
    async def get_users(self,session:AsyncSession =Depends(get_session)):
        statement =  select(User).order_by(desc(User.created_at))
        result = await  session.execute(statement)
        
        return  result.scalars().all()
    async def get_user_by_uid(self,user_uid:str,session:AsyncSession = Depends(get_session)):
        try:
            uid_obj = uuid.UUID(user_uid)
        except ValueError:
            return None    
        statement = select(User).where(User.uid == uid_obj)
        result =  await session.execute(statement)
        
        user = result.scalars().first()
        return  user if user is not None else None
        
    
    async def update_user(self,user_uid:str , user_data: dict, session:AsyncSession=  Depends(get_session) ):
        user =await self.get_user_by_uid(user_uid,session)
        if not user:
            return None
        for name , value  in  user_data.items():
            if hasattr(user,name):
               setattr(user,name,value)
        await session.commit()
        await session.refresh(user)
        
         # Publish update event
        # event_publisher.publish_event("user.v1.updated", {
        #    "user_id": str(user.uid),
        #    "username": user.username,
        #    "email": user.email,
        #    "name": user.name,
        #    "is_active": user.is_active,
        #    "role": user.role.value
        # })
        return user  
    
    async def delete_user(self,user_uid :str,session:AsyncSession =Depends(get_session)):
        user = await self.get_user_uid(user_uid,session)
        if user is not None :
            await session.delete(user)
            await  session.commit()
            
             # Publish delete event
            # event_publisher.publish_event("user.v1.deleted", {
            #   "user_id": str(user_uid)
            # })
            return {}
        else :
            return None
    
    