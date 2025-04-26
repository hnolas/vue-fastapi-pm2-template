from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.api.auth import get_current_user
from app.db import get_db
from app.models.participant import Participant
from app.schemas.participant import (
    ParticipantCreate,
    ParticipantResponse,
    ParticipantUpdate,
)

router = APIRouter(tags=["participants"], prefix="/participants")


@router.post("/", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
async def create_participant(
    participant: ParticipantCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Create a new participant"""
    # Check if participant with PID already exists
    result = await db.execute(select(Participant).where(Participant.pid == participant.pid))
    existing_participant = result.scalars().first()
    
    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Participant with PID {participant.pid} already exists"
        )
    
    # Create new participant
    new_participant = Participant(**participant.model_dump())
    db.add(new_participant)
    await db.commit()
    await db.refresh(new_participant)
    
    return new_participant


@router.get("/", response_model=List[ParticipantResponse])
async def get_participants(
    skip: int = 0,
    limit: int = 100,
    active: Optional[bool] = None,
    study_group: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Get all participants with optional filtering"""
    query = select(Participant)
    
    if active is not None:
        query = query.where(Participant.active == active)
    
    if study_group:
        query = query.where(Participant.study_group == study_group)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    participants = result.scalars().all()
    
    return participants


@router.get("/{participant_id}", response_model=ParticipantResponse)
async def get_participant(
    participant_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Get a specific participant by ID"""
    result = await db.execute(select(Participant).where(Participant.id == participant_id))
    participant = result.scalars().first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant with ID {participant_id} not found"
        )
    
    return participant


@router.get("/by-pid/{pid}", response_model=ParticipantResponse)
async def get_participant_by_pid(
    pid: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Get a specific participant by PID"""
    result = await db.execute(select(Participant).where(Participant.pid == pid))
    participant = result.scalars().first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant with PID {pid} not found"
        )
    
    return participant


@router.put("/{participant_id}", response_model=ParticipantResponse)
async def update_participant(
    participant_id: int,
    participant_update: ParticipantUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Update a participant"""
    # Check if participant exists
    result = await db.execute(select(Participant).where(Participant.id == participant_id))
    existing_participant = result.scalars().first()
    
    if not existing_participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant with ID {participant_id} not found"
        )
    
    # Update participant
    update_data = participant_update.model_dump(exclude_unset=True)
    
    await db.execute(
        update(Participant)
        .where(Participant.id == participant_id)
        .values(**update_data)
    )
    
    await db.commit()
    
    # Get updated participant
    result = await db.execute(select(Participant).where(Participant.id == participant_id))
    updated_participant = result.scalars().first()
    
    return updated_participant


@router.delete("/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_participant(
    participant_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Delete a participant"""
    # Check if participant exists
    result = await db.execute(select(Participant).where(Participant.id == participant_id))
    existing_participant = result.scalars().first()
    
    if not existing_participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant with ID {participant_id} not found"
        )
    
    # Delete participant
    await db.execute(delete(Participant).where(Participant.id == participant_id))
    await db.commit()
    
    return None
