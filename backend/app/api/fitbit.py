from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.api.auth import get_current_user
from app.db import get_db
from app.models.participant import Participant
from app.models.fitbit import FitbitToken
from app.schemas.fitbit import FitbitTokenResponse, FitbitAuthRequest
from app.services.fitbit_service import get_fitbit_auth_url, get_tokens_from_code

router = APIRouter(tags=["fitbit"], prefix="/fitbit")


@router.post("/registration-request/{participant_id}", status_code=status.HTTP_200_OK)
async def register_fitbit_request(
    participant_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Mark a participant as needing Fitbit registration"""
    # Check if participant exists
    result = await db.execute(select(Participant).where(Participant.id == participant_id))
    participant = result.scalars().first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant with ID {participant_id} not found"
        )
    
    # Update participant to indicate fitbit registration is needed
    await db.execute(
        update(Participant)
        .where(Participant.id == participant_id)
        .values(fitbit_registration_requested=True)
    )
    
    await db.commit()
    
    return {"message": f"Fitbit registration requested for participant {participant_id}"}


@router.get("/login")
async def fitbit_login(
    pid: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint: Start Fitbit OAuth flow"""
    # Check if participant exists
    result = await db.execute(select(Participant).where(Participant.pid == pid))
    participant = result.scalars().first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant with PID {pid} not found"
        )
    
    # Check if registration was requested
    if not participant.fitbit_registration_requested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fitbit registration has not been requested for this participant"
        )
    
    # Get auth URL for Fitbit OAuth
    auth_url = get_fitbit_auth_url(participant.pid, str(request.base_url))
    
    return RedirectResponse(auth_url)


@router.get("/callback")
async def fitbit_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint: Handle Fitbit OAuth callback"""
    # The state should contain the PID
    pid = state
    
    # Check if participant exists
    result = await db.execute(select(Participant).where(Participant.pid == pid))
    participant = result.scalars().first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant with PID {pid} not found"
        )
    
    # Exchange code for tokens
    token_data = get_tokens_from_code(code)
    
    # Check if participant already has tokens
    token_result = await db.execute(
        select(FitbitToken).where(FitbitToken.participant_id == participant.id)
    )
    existing_token = token_result.scalars().first()
    
    if existing_token:
        # Update existing token
        existing_token.access_token = token_data["access_token"]
        existing_token.refresh_token = token_data["refresh_token"]
        existing_token.expires_at = token_data["expires_at"]
    else:
        # Create new token record
        token = FitbitToken(
            participant_id=participant.id,
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_at=token_data["expires_at"],
        )
        db.add(token)
    
    # Update participant to indicate fitbit is connected
    await db.execute(
        update(Participant)
        .where(Participant.id == participant.id)
        .values(fitbit_connected=True)
    )
    
    await db.commit()
    
    # Display thank you page (this would be a proper HTML page in production)
    return {
        "message": "Thank you for connecting your Fitbit! You may close this window now.",
        "success": True
    }


@router.get("/tokens", response_model=list[FitbitTokenResponse])
async def get_fitbit_tokens(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Get all Fitbit tokens (for admin/research use)"""
    result = await db.execute(select(FitbitToken))
    tokens = result.scalars().all()
    
    return tokens


@router.post("/fetch-data", status_code=status.HTTP_202_ACCEPTED)
async def trigger_fitbit_data_fetch(
    participant_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Trigger Fitbit data fetch for one or all participants"""
    # This is a stub for the actual implementation
    # In a real system, this would queue a task to fetch Fitbit data
    if participant_id:
        # Check if participant exists
        result = await db.execute(select(Participant).where(Participant.id == participant_id))
        participant = result.scalars().first()
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Participant with ID {participant_id} not found"
            )
        
        message = f"Fitbit data fetch triggered for participant {participant_id}"
    else:
        message = "Fitbit data fetch triggered for all participants"
    
    return {"message": message}


@router.post("/auth", response_model=dict)
async def create_fitbit_auth(
    auth_data: FitbitAuthRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """Manually create Fitbit auth for a participant (admin function)"""
    # Check if participant exists
    result = await db.execute(select(Participant).where(Participant.id == auth_data.participant_id))
    participant = result.scalars().first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant with ID {auth_data.participant_id} not found"
        )
    
    # Check if token already exists
    token_result = await db.execute(
        select(FitbitToken).where(FitbitToken.participant_id == participant.id)
    )
    existing_token = token_result.scalars().first()
    
    if existing_token:
        # Update existing token
        existing_token.access_token = auth_data.access_token
        existing_token.refresh_token = auth_data.refresh_token
        existing_token.expires_at = auth_data.expires_at
    else:
        # Create new token
        token = FitbitToken(
            participant_id=participant.id,
            access_token=auth_data.access_token,
            refresh_token=auth_data.refresh_token,
            expires_at=auth_data.expires_at,
        )
        db.add(token)
    
    # Update participant to indicate fitbit is connected
    await db.execute(
        update(Participant)
        .where(Participant.id == participant.id)
        .values(fitbit_connected=True)
    )
    
    await db.commit()
    
    return {"message": f"Fitbit auth created for participant {participant.id}"}
