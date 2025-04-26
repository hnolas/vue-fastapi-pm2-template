from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.api.auth import get_current_user
from app.db import get_db
from app.models.message import MessageContent
from app.schemas.message import (
    MessageContentCreate,
    MessageContentResponse,
    MessageContentUpdate,
)

router = APIRouter(tags=["message_content"], prefix="/message-content")


@router.post("/", response_model=MessageContentResponse, status_code=status.HTTP_201_CREATED)
async def create_message_content(
    message_content: MessageContentCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Create a new message content/template"""
    # Create new message content
    new_message_content = MessageContent(**message_content.model_dump())
    db.add(new_message_content)
    await db.commit()
    await db.refresh(new_message_content)
    
    return new_message_content


@router.get("/", response_model=List[MessageContentResponse])
async def get_message_contents(
    skip: int = 0,
    limit: int = 100,
    bucket: Optional[str] = None,
    active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Get all message content/templates with optional filtering"""
    query = select(MessageContent)
    
    if bucket:
        query = query.where(MessageContent.bucket == bucket)
    
    if active is not None:
        query = query.where(MessageContent.active == active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    message_contents = result.scalars().all()
    
    return message_contents


@router.get("/{message_content_id}", response_model=MessageContentResponse)
async def get_message_content(
    message_content_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Get a specific message content/template by ID"""
    result = await db.execute(select(MessageContent).where(MessageContent.id == message_content_id))
    message_content = result.scalars().first()
    
    if not message_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message content with ID {message_content_id} not found"
        )
    
    return message_content


@router.put("/{message_content_id}", response_model=MessageContentResponse)
async def update_message_content(
    message_content_id: int,
    message_content_update: MessageContentUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Update a message content/template"""
    # Check if message content exists
    result = await db.execute(select(MessageContent).where(MessageContent.id == message_content_id))
    existing_message_content = result.scalars().first()
    
    if not existing_message_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message content with ID {message_content_id} not found"
        )
    
    # Update message content
    update_data = message_content_update.model_dump(exclude_unset=True)
    
    await db.execute(
        update(MessageContent)
        .where(MessageContent.id == message_content_id)
        .values(**update_data)
    )
    
    await db.commit()
    
    # Get updated message content
    result = await db.execute(select(MessageContent).where(MessageContent.id == message_content_id))
    updated_message_content = result.scalars().first()
    
    return updated_message_content


@router.delete("/{message_content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message_content(
    message_content_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Delete a message content/template"""
    # Check if message content exists
    result = await db.execute(select(MessageContent).where(MessageContent.id == message_content_id))
    existing_message_content = result.scalars().first()
    
    if not existing_message_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message content with ID {message_content_id} not found"
        )
    
    # Delete message content
    await db.execute(delete(MessageContent).where(MessageContent.id == message_content_id))
    await db.commit()
    
    return None


@router.get("/buckets/unique", response_model=List[str])
async def get_unique_buckets(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Get all unique bucket names used in message content"""
    result = await db.execute(select(MessageContent.bucket).distinct())
    buckets = [row[0] for row in result.all()]
    
    return buckets