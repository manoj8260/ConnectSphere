"""update message and room model

Revision ID: 2e237bcf8070
Revises: 806efae0df9a
Create Date: 2025-09-17 23:37:35.869008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# --- Manual Addition ---
# Import your MessageType Enum. Adjust the path if it's different in your project.
from chat.schema.message import MessageType 

# revision identifiers, used by Alembic.
revision: str = '2e237bcf8070'
down_revision: Union[str, Sequence[str], None] = '806efae0df9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# --- Manual Addition ---
# Define the PostgreSQL ENUM type using your Python Enum
# create_type=False prevents it from being created automatically on table creation
messagetype_enum = postgresql.ENUM(MessageType, name='messagetype', create_type=False)


def upgrade() -> None:
    """Upgrade schema."""
    # ### Manually adjusted commands ###
    
    # 1. Create the custom ENUM type in PostgreSQL
    messagetype_enum.create(op.get_bind(), checkfirst=True)
    
    # 2. Alter the column to use the new ENUM type
    op.alter_column('messages', 'message_type',
        existing_type=sa.VARCHAR(length=20),
        type_=messagetype_enum,
        existing_nullable=False,
        postgresql_using='message_type::text::messagetype' # Cast existing data to the new type
    )
    
    # 3. Perform the rest of the schema changes
    op.create_index(op.f('ix_messages_room_id'), 'messages', ['room_id'], unique=False)
    op.drop_column('messages', 'username')
    op.drop_column('rooms', 'message_count')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### Manually adjusted commands ###
    
    # 1. Add columns back first
    op.add_column('rooms', sa.Column('message_count', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('messages', sa.Column('username', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    
    # 2. Drop the index
    op.drop_index(op.f('ix_messages_room_id'), table_name='messages')
    
    # 3. Alter the column back to VARCHAR before dropping the ENUM
    op.alter_column('messages', 'message_type',
        existing_type=messagetype_enum,
        type_=sa.VARCHAR(length=20),
        existing_nullable=False
    )
    
    # 4. Drop the custom ENUM type from PostgreSQL
    messagetype_enum.drop(op.get_bind(), checkfirst=True)
    # ### end Alembic commands ###