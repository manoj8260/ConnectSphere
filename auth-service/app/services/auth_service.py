from  sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.schemas.auth_schema import SignupModel
from app.models.user_model import User
from app.core.utils import generate_password_hash


class  AuthServices:
    
    @staticmethod
    async def get_user_by_email(email:str,session:AsyncSession):
       """Fetch a user by email (or return None if not found)."""
       statement =  select(User).where(User.email==email)
       
       result = await session.execute(statement)
       
       user = result.scalars().first()
       return user
   
    
    async def user_exists(self,email:str,session:AsyncSession):
       """Check if a user with this email exists.""" 
       get_user=  await  self.get_user_by_email(email,session)
       return  get_user is not None
        
   
       
    
    async def create_user(self,user_data:SignupModel,session:AsyncSession):
        """Create a new user with hashed password."""
        user_data_dict = user_data.model_dump()
        username = user_data_dict['email'].split('@')[0]
        
        
        new_user = User(**user_data_dict,username=username,role="user")
        new_user.password = generate_password_hash(user_data_dict.get('password'))
        
        session.add(new_user)
        await  session.commit()
        await session.refresh(new_user)
        return new_user
        