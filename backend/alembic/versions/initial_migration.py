"""Initial migration

Revision ID: 1a1c3b5d6e7f
Revises: 
Create Date: 2023-09-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1a1c3b5d6e7f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create participant table
    op.create_table(
        'participant',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('pid', sa.String(100), nullable=False),
        sa.Column('friendly_name', sa.String(100), nullable=True),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('study_group', sa.String(50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('sms_window_start', sa.Time(), nullable=True),
        sa.Column('sms_window_end', sa.Time(), nullable=True),
        sa.Column('timezone_offset', sa.Integer(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('fitbit_connected', sa.Boolean(), nullable=False, default=False),
        sa.Column('fitbit_registration_requested', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_participant_id'), 'participant', ['id'], unique=False)
    op.create_index(op.f('ix_participant_pid'), 'participant', ['pid'], unique=True)
    
    # Create messagecontent table
    op.create_table(
        'messagecontent',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('bucket', sa.String(50), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messagecontent_id'), 'messagecontent', ['id'], unique=False)
    op.create_index(op.f('ix_messagecontent_bucket'), 'messagecontent', ['bucket'], unique=False)
    
    # Create message table
    op.create_table(
        'message',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('bucket', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('sent_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('delivered_datetime', sa.DateTime(timezone=True), nullable=True),
        sa.Column('twilio_sid', sa.String(50), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['participant_id'], ['participant.id']),
        sa.ForeignKeyConstraint(['content_id'], ['messagecontent.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_id'), 'message', ['id'], unique=False)
    op.create_index(op.f('ix_message_status'), 'message', ['status'], unique=False)
    
    # Create fitbittoken table
    op.create_table(
        'fitbittoken',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=False),
        sa.Column('access_token', sa.String(1000), nullable=False),
        sa.Column('refresh_token', sa.String(1000), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['participant_id'], ['participant.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('participant_id')
    )
    op.create_index(op.f('ix_fitbittoken_id'), 'fitbittoken', ['id'], unique=False)
    
    # Create fitbitdata table
    op.create_table(
        'fitbitdata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('token_id', sa.Integer(), nullable=False),
        sa.Column('data_type', sa.String(50), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('exported', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['token_id'], ['fitbittoken.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fitbitdata_id'), 'fitbitdata', ['id'], unique=False)
    op.create_index(op.f('ix_fitbitdata_data_type'), 'fitbitdata', ['data_type'], unique=False)
    op.create_index(op.f('ix_fitbitdata_date'), 'fitbitdata', ['date'], unique=False)


def downgrade() -> None:
    op.drop_table('fitbitdata')
    op.drop_table('fitbittoken')
    op.drop_table('message')
    op.drop_table('messagecontent')
    op.drop_table('participant')
