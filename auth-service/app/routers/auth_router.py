from app.core.config import Config
from datetime import timedelta ,datetime ,timezone
from app.database.connection import get_session
from app.models.user_model import User
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.schemas.auth_schema import SignupModel, SignInModel
from app.services.auth_service import AuthServices
from app.core.utils import verify_password ,create_token
from app.database.redis import blacklist_token,is_token_blacklisted
from app.core.errors import UserAleradyExists
from app.core.dependency import (TokenBearer,AccessTokenBearer,RefreshTokenBearer  ,login_required)


#router
auth_router = APIRouter()
#serises
auth_services = AuthServices()
# dependecies
token_bearer = TokenBearer()
access_token = AccessTokenBearer()
refresh_token = RefreshTokenBearer()

@auth_router.post('/register', response_model=User)
async def signup(user: SignupModel, session: AsyncSession = Depends(get_session)):
    exist_user = await auth_services.user_exists(email=user.email, session=session)
    if exist_user:
         raise UserAleradyExists()
    new_user = await auth_services.create_user(user, session)
    return new_user

@auth_router.post('/login')
async def signup(login_data:SignInModel,session:AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password
    user = await auth_services.get_user_by_email(email,session)
    if user is not None :
      verify_pass = verify_password(password,user.password)
      if verify_pass:
        access_token = create_token(
            user_data=
            {
                'email' : user.email,
                'uid': str(user.uid),
                "username" : user.username,
            }
        )
        refresh_token =  create_token(
            {
                'email' : user.email,
                'uid' :  str(user.uid)
            },
            expire_delta= timedelta(days=Config.REFRESH_TOKEN_EXPIRE),
            refresh=True
        )
        return  JSONResponse(
            content= {
                'message' : 'Login Sucessfully',
                'user' : 
                    {
                  'email' : user.email,
                  'uid' :  str(user.uid)
                },
                'access_token' : str(access_token)  ,
                'refresh_token' : str(refresh_token) 
            },
            status_code=200,
            
        )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='crendential does not match')  

@auth_router.get('/refresh',status_code=status.HTTP_200_OK)
async  def get_access_token(token_details: dict = Depends(refresh_token)):
    jti =  token_details.get('jti')
    expairy_timestamp = token_details.get('exp')
   
    if  datetime.fromtimestamp(expairy_timestamp ,tz=timezone.utc) <= datetime.utcnow().replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='invalid and expiry token')
    
    access_token= create_token(
         user_data= token_details.get('user'),
         expire_delta= timedelta(seconds=Config.ACCESS_TOKEN_EXPIRE),
         refresh= False
       )
       
    return {
         'new_access_token' : access_token
       }
   


@auth_router.post('/logout')
async def signout(token_data:dict = Depends(refresh_token)):
    jti = token_data['jti']
    await blacklist_token(jti)
    return    JSONResponse(
       {
          'message' : 'Logged out sucessfully'
       } , status_code= status.HTTP_200_OK
   ) 



@auth_router.get('/me',status_code=status.HTTP_200_OK)
async  def current_user(user = Depends(login_required)):
   return {
        "message": f"Hello {user.name}, welcome home page!",
        "email": user.email,
    }  
