import uuid
from sqlmodel import SQLModel,Field ,Column ,Relationship
from sqlalchemy.dialects import postgresql as pg
from datetime import datetime
from typing import List
from enum import Enum as PyEnum
from sqlalchemy import Enum

class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class User(SQLModel,table=True):
    __tablename__ ='users'
    uid :uuid.UUID =  Field(
        default_factory= uuid.uuid4,
        sa_column=Column(pg.UUID(as_uuid=True) , primary_key=True,nullable=False)
    )
    username: str = Field(sa_column=Column(pg.VARCHAR(50), nullable=False, unique=True))
    email: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False, unique=True,index=True))
    name: str = Field(sa_column=Column(pg.VARCHAR(100), nullable=False))
    
    password : str =  Field(sa_column=Column(pg.VARCHAR,nullable=False),exclude=True)
    is_active : bool = Field(default=False,index=True)
    role : UserRole = Field(
        sa_column=Column(Enum(UserRole,name="user_role_enum"),default=UserRole.USER,nullable=False,index=True))
    
    created_at : datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True),default =datetime.utcnow))
    updated_at : datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True),default =datetime.utcnow,onupdate=datetime.utcnow))
    

    
        

    
    
    