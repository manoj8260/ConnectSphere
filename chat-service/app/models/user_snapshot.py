# chat-service/app/models/user_snapshot.py
import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects import postgresql as pg

class UserSnapshot(SQLModel, table=True):
    """Local cache of user info from auth-service"""
    __tablename__ = "user_snapshots"

    user_id: uuid.UUID = Field(
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True, nullable=False)
    )
    username: str = Field(sa_column=Column(pg.VARCHAR(50), nullable=False))
    email: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    name: str = Field(sa_column=Column(pg.VARCHAR(100), nullable=False))
    is_active: bool = Field(default=True)
    role: str = Field(sa_column=Column(pg.VARCHAR(20), nullable=False, default="user"))
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    )

class ProcessedEvent(SQLModel, table=True):
    """Track processed events for idempotency"""
    __tablename__ = "processed_events"
    
    event_id: str = Field(primary_key=True, max_length=36)
    event_type: str = Field(sa_column=Column(pg.VARCHAR(100), nullable=False))
    processed_at: datetime = Field(default_factory=datetime.utcnow)