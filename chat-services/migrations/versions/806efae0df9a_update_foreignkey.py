"""update foreignkey 

Revision ID: 806efae0df9a
Revises: 
Create Date: 2025-09-17 22:57:52.334837
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg


# revision identifiers, used by Alembic.
revision: str = '806efae0df9a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add new room_name column first
    op.add_column("rooms", sa.Column("room_name", sa.VARCHAR(length=100), nullable=False))
    op.drop_index(op.f("ix_rooms_room_id"), table_name="rooms")
    op.create_index(op.f("ix_rooms_room_name"), "rooms", ["room_name"], unique=True)
    op.drop_column("rooms", "room_id")

    # --- FIX for room_id type conversion ---
    # Add a temporary UUID column
    op.add_column("messages", sa.Column("room_id_tmp", pg.UUID, nullable=True))

    # Copy data: if old messages.room_id contained UUID strings
    op.execute("UPDATE messages SET room_id_tmp = room_id::uuid")

    # If instead it contained room names, you need:
    # op.execute("""
    #     UPDATE messages m
    #     SET room_id_tmp = r.rid
    #     FROM rooms r
    #     WHERE m.room_id = r.room_name
    # """)

    # Drop old column
    op.drop_column("messages", "room_id")

    # Rename tmp column
    op.alter_column("messages", "room_id_tmp", new_column_name="room_id", existing_type=pg.UUID, nullable=False)

    # Add FK
    op.create_foreign_key("fk_messages_room", "messages", "rooms", ["room_id"], ["rid"], ondelete="CASCADE")


def downgrade() -> None:
    """Downgrade schema."""

    # Recreate old column
    op.add_column("rooms", sa.Column("room_id", sa.VARCHAR(length=100), nullable=False))
    op.drop_index(op.f("ix_rooms_room_name"), table_name="rooms")
    op.create_index(op.f("ix_rooms_room_id"), "rooms", ["room_id"], unique=True)
    op.drop_column("rooms", "room_name")

    op.drop_constraint("fk_messages_room", "messages", type_="foreignkey")

    # Add old VARCHAR column back
    op.add_column("messages", sa.Column("room_id_tmp", sa.VARCHAR(length=100), nullable=True))

    # Restore data
    op.execute("UPDATE messages SET room_id_tmp = room_id::text")

    op.drop_column("messages", "room_id")
    op.alter_column("messages", "room_id_tmp", new_column_name="room_id", existing_type=sa.VARCHAR(100), nullable=False)
