from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select 
from fastapi import HTTPException ,Depends
from app.models.user_snapshot import UserSnapshot
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

class UserSnapshotService:
    """
    Handles creation and updating of local user snapshots from auth-service.
    """

    async def get_snapshot(self, session: AsyncSession, user_id: uuid.UUID) -> UserSnapshot | None:
        """Fetch a snapshot by user_id"""
        try:
            statement = select(UserSnapshot).where(UserSnapshot.user_id == user_id)
            result = await session.execute(statement)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching user snapshot: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch user snapshot")

    async def upsert_snapshot(self, session: AsyncSession, user_data: dict) -> UserSnapshot:
      try:
        user_id = user_data.get("user_id")
        if not isinstance(user_id, uuid.UUID):
            raise ValueError("Invalid user_id: Must be UUID")

        snapshot = await self.get_snapshot(session, user_id)

        if snapshot is not None:
            # Update existing snapshot
            snapshot.username = user_data.get("username", snapshot.username)
            snapshot.email = user_data.get("email", snapshot.email)
            snapshot.name = user_data.get("name", snapshot.name)
            snapshot.role = user_data.get("role", snapshot.role)
            snapshot.is_active = user_data.get("is_active", snapshot.is_active)
            snapshot.updated_at = datetime.utcnow()
        else:
            # Create new snapshot
            snapshot = UserSnapshot(
                user_id=user_id,
                username=user_data["username"],
                email=user_data["email"],
                name=user_data.get("name", ""),
                role=user_data.get("role", "member"),
                is_active=user_data.get("is_active", True),
                updated_at=datetime.utcnow(),
            )
            session.add(snapshot)
            await session.flush()

        # ✅ Return snapshot in both cases
        return snapshot

      except ValueError as e:
        await session.rollback()
        logger.warning(f"Validation error in upsert_snapshot: {e}")
        raise HTTPException(status_code=400, detail=str(e))
      except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Database error in upsert_snapshot: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user snapshot")
      except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error in upsert_snapshot: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error in snapshot update")


async def get_user_snapshot_service() -> UserSnapshotService:
    return UserSnapshotService()
