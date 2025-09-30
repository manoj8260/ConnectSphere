from pydantic import BaseModel
import uuid
from datetime import datetime
from app.models.user_model import UserRole
from typing import Optional

class UserRead(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    name: str
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: datetime
    
    class Config:
      from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
        

      