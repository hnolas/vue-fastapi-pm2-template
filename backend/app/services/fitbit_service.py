"""
Fitbit Service - Handles Fitbit OAuth and data synchronization
"""
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

import httpx
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
try:
    from dropbox import Dropbox
    from dropbox.files import WriteMode
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False

from app.core.config import settings
from app.models.participant import Participant
from app.models.fitbit import FitbitToken, FitbitData

logger = logging.getLogger(__name__)

# Fitbit API constants
FITBIT_AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
FITBIT_TOKEN_URL = "https://api.fitbit.com/oauth2/token"
FITBIT_API_BASE_URL = "https://api.fitbit.com/1"

# Scopes needed for our application
SCOPES = [
    "activity",
    "heartrate",
    "location",
    "nutrition",
    "profile",
    "settings",
    "sleep",
    "social",
    "weight"
]


def get_fitbit_auth_url(state: str, redirect_base_url: str) -> str:
    """
    Generate the Fitbit OAuth authorization URL
    
    Args:
        state: State parameter to include in the URL (usually the participant PID)
        redirect_base_url: The base URL for the redirect
        
    Returns:
        The authorization URL to redirect the user to
    """
    # Build the callback URL
    callback_url = f"{redirect_base_url}api/fitbit/callback"
    
    # Build the auth URL
    params = {
        "client_id": settings.FITBIT_CLIENT_ID,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "redirect_uri": callback_url,
        "state": state  # Use PID as state
    }
    
    auth_url = f"{FITBIT_AUTH_URL}?{urlencode(params)}"
    return auth_url


def get_tokens_from_code(code: str, redirect_base_url: str = "http://localhost:8000/") -> Dict[str, Any]:
    """
    Exchange authorization code for access and refresh tokens
    
    Args:
        code: Authorization code from Fitbit
        redirect_base_url: The base URL for the redirect
        
    Returns:
        Dictionary with access_token, refresh_token, and expires_at
    """
    # Build the callback URL - must match the one used in the authorization request
    callback_url = f"{redirect_base_url}api/fitbit/callback"
    
    # Exchange code for tokens
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        # Basic auth with client ID and secret
        "Authorization": f"Basic {get_basic_auth_header()}"
    }
    
    data = {
        "client_id": settings.FITBIT_CLIENT_ID,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": callback_url
    }
    
    with httpx.Client() as client:
        response = client.post(FITBIT_TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
    
    # Calculate expiration time
    expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
    
    return {
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "expires_at": expires_at
    }


def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """
    Refresh an expired access token
    
    Args:
        refresh_token: The refresh token
        
    Returns:
        Dictionary with new access_token, refresh_token, and expires_at
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {get_basic_auth_header()}"
    }
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    with httpx.Client() as client:
        response = client.post(FITBIT_TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
    
    # Calculate expiration time
    expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
    
    return {
        "access_token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token", refresh_token),  # Use old one if not provided
        "expires_at": expires_at
    }


def get_basic_auth_header() -> str:
    """
    Generate the Basic Auth header value for Fitbit API
    
    Returns:
        Base64 encoded header value
    """
    import base64
    
    auth_string = f"{settings.FITBIT_CLIENT_ID}:{settings.FITBIT_CLIENT_SECRET}"
    encoded = base64.b64encode(auth_string.encode()).decode()
    
    return encoded


async def fetch_participant_data(token: FitbitToken, date: datetime = None, types: List[str] = None) -> List[FitbitData]:
    """
    Fetch data for a specific participant on a specific date
    
    Args:
        token: FitbitToken instance
        date: The date to fetch data for (defaults to today)
        types: List of data types to fetch (defaults to all)
        
    Returns:
        List of FitbitData instances
    """
    if date is None:
        date = datetime.utcnow().date()
        
    if types is None:
        types = ["steps", "heartrate", "sleep", "activities"]
    
    data_points = []
    
    # Check if token is expired and refresh if needed
    if token.expires_at <= datetime.utcnow() + timedelta(minutes=5):
        try:
            new_tokens = refresh_access_token(token.refresh_token)
            token.access_token = new_tokens["access_token"]
            token.refresh_token = new_tokens["refresh_token"]
            token.expires_at = new_tokens["expires_at"]
            # Token would be updated in the database by the caller
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return data_points
    
    # Prepare headers with access token
    headers = {
        "Authorization": f"Bearer {token.access_token}"
    }
    
    formatted_date = date.strftime("%Y-%m-%d")
    
    try:
        with httpx.Client() as client:
            for data_type in types:
                if data_type == "steps":
                    # Fetch steps data
                    url = f"{FITBIT_API_BASE_URL}/user/-/activities/steps/date/{formatted_date}/1d.json"
                    response = client.get(url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    data_points.append(FitbitData(
                        token_id=token.id,
                        data_type="steps",
                        date=date,
                        data=data
                    ))
                
                elif data_type == "heartrate":
                    # Fetch heart rate data
                    url = f"{FITBIT_API_BASE_URL}/user/-/activities/heart/date/{formatted_date}/1d.json"
                    response = client.get(url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    data_points.append(FitbitData(
                        token_id=token.id,
                        data_type="heartrate",
                        date=date,
                        data=data
                    ))
                
                elif data_type == "sleep":
                    # Fetch sleep data
                    url = f"{FITBIT_API_BASE_URL}/user/-/sleep/date/{formatted_date}.json"
                    response = client.get(url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    data_points.append(FitbitData(
                        token_id=token.id,
                        data_type="sleep",
                        date=date,
                        data=data
                    ))
                
                elif data_type == "activities":
                    # Fetch activity summary
                    url = f"{FITBIT_API_BASE_URL}/user/-/activities/date/{formatted_date}.json"
                    response = client.get(url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    data_points.append(FitbitData(
                        token_id=token.id,
                        data_type="activities",
                        date=date,
                        data=data
                    ))
    
    except Exception as e:
        logger.error(f"Error fetching Fitbit data: {e}")
    
    return data_points


async def sync_all_participants_data(db: AsyncSession, date: datetime = None) -> int:
    """
    Sync data for all participants with Fitbit connections
    
    Args:
        db: Database session
        date: The date to fetch data for (defaults to today)
        
    Returns:
        Number of data points synced
    """
    if date is None:
        date = datetime.utcnow().date()
    
    # Get all active participants with Fitbit connections
    query = select(Participant).where(
        and_(
            Participant.active == True,
            Participant.fitbit_connected == True
        )
    )
    result = await db.execute(query)
    participants = result.scalars().all()
    
    total_synced = 0
    
    for participant in participants:
        # Get token for participant
        token_query = select(FitbitToken).where(FitbitToken.participant_id == participant.id)
        token_result = await db.execute(token_query)
        token = token_result.scalars().first()
        
        if not token:
            logger.warning(f"Participant {participant.id} marked as connected but no token found")
            continue
        
        # Fetch data for participant
        data_points = await fetch_participant_data(token, date)
        
        # Save data points to database
        for data_point in data_points:
            db.add(data_point)
            total_synced += 1
        
        # Update token if it was refreshed
        db.add(token)
    
    await db.commit()
    
    return total_synced


async def export_data_to_dropbox(db: AsyncSession) -> int:
    """
    Export Fitbit data to Dropbox
    
    Args:
        db: Database session
        
    Returns:
        Number of data points exported
    """
    if not settings.DROPBOX_ACCESS_TOKEN:
        logger.warning("Dropbox access token not configured")
        return 0
    
    if not DROPBOX_AVAILABLE:
        logger.warning("Dropbox package not installed")
        return 0
    
    # Get all unexported data
    query = select(FitbitData).where(FitbitData.exported == False)
    result = await db.execute(query)
    data_points = result.scalars().all()
    
    if not data_points:
        logger.info("No new data to export")
        return 0
    
    try:
        # Connect to Dropbox
        dbx = Dropbox(settings.DROPBOX_ACCESS_TOKEN)
        
        # Group data by participant and date
        by_token_id = {}
        for data_point in data_points:
            if data_point.token_id not in by_token_id:
                by_token_id[data_point.token_id] = []
            by_token_id[data_point.token_id].append(data_point)
        
        exported_count = 0
        
        # For each participant, create a combined file
        for token_id, token_data_points in by_token_id.items():
            # Get participant info
            token_query = select(FitbitToken).where(FitbitToken.id == token_id)
            token_result = await db.execute(token_query)
            token = token_result.scalars().first()
            
            if not token:
                logger.warning(f"Token {token_id} not found")
                continue
            
            participant_query = select(Participant).where(Participant.id == token.participant_id)
            participant_result = await db.execute(participant_query)
            participant = participant_result.scalars().first()
            
            if not participant:
                logger.warning(f"Participant for token {token_id} not found")
                continue
            
            # Group by date
            by_date = {}
            for data_point in token_data_points:
                date_str = data_point.date.strftime("%Y-%m-%d")
                if date_str not in by_date:
                    by_date[date_str] = {}
                
                by_date[date_str][data_point.data_type] = data_point.data
            
            # Upload each date's data
            for date_str, date_data in by_date.items():
                file_path = f"{settings.FITBIT_DATA_EXPORT_PATH}/{participant.pid}/{date_str}.json"
                file_content = json.dumps(date_data, indent=2).encode()
                
                try:
                    dbx.files_upload(
                        file_content,
                        file_path,
                        mode=WriteMode.overwrite
                    )
                    
                    # Mark data points as exported
                    for data_point in token_data_points:
                        if data_point.date.strftime("%Y-%m-%d") == date_str:
                            data_point.exported = True
                            exported_count += 1
                
                except Exception as e:
                    logger.error(f"Error uploading to Dropbox: {e}")
        
        # Commit changes
        await db.commit()
        
        return exported_count
    
    except Exception as e:
        logger.error(f"Error exporting to Dropbox: {e}")
        return 0