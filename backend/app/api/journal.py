"""
Journal API endpoints for daily notes.
"""

from __future__ import annotations

from datetime import date, datetime, UTC
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.auth import get_current_active_user
from .. import models
from ..models.daily_note import DailyNote
from ..schemas.journal import (
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryResponse,
)


router = APIRouter(prefix="/journal", tags=["Journal"])


@router.post("/{entry_date}", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_journal_entry(
    entry_date: date = Path(..., description="Date for journal entry (YYYY-MM-DD)"),
    payload: JournalEntryCreate = ...,
    db: Session = Depends(get_db),
    # TEMPORARY: Auth disabled for development - Remove this comment when auth is ready
    # current_user: models.User = Depends(get_current_active_user),
) -> JournalEntryResponse:
    """
    Create or update a journal entry for a specific date.

    If an entry already exists for this date, it will be updated.
    Otherwise, a new entry will be created.
    """
    # TEMPORARY: Hardcoded user_id for development
    user_id = 1

    # Check if entry already exists for this date
    existing_entry = db.query(DailyNote).filter(
        DailyNote.user_id == user_id,
        DailyNote.note_date == entry_date
    ).first()

    if existing_entry:
        # Update existing entry
        existing_entry.note_text = payload.note_text
        existing_entry.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(existing_entry)
        return existing_entry
    else:
        # Create new entry
        new_entry = DailyNote(
            user_id=user_id,
            note_date=entry_date,
            note_text=payload.note_text
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        return new_entry


@router.get("/{entry_date}", response_model=Optional[JournalEntryResponse])
async def get_journal_entry(
    entry_date: date = Path(..., description="Date for journal entry (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    # TEMPORARY: Auth disabled for development
    # current_user: models.User = Depends(get_current_active_user),
) -> Optional[JournalEntryResponse]:
    """
    Get journal entry for a specific date.

    Returns null if no entry exists for this date.
    """
    # TEMPORARY: Hardcoded user_id for development
    user_id = 1

    entry = db.query(DailyNote).filter(
        DailyNote.user_id == user_id,
        DailyNote.note_date == entry_date
    ).first()

    return entry


@router.delete("/{entry_date}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal_entry(
    entry_date: date = Path(..., description="Date for journal entry (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    # TEMPORARY: Auth disabled for development
    # current_user: models.User = Depends(get_current_active_user),
):
    """
    Delete journal entry for a specific date.
    """
    # TEMPORARY: Hardcoded user_id for development
    user_id = 1

    entry = db.query(DailyNote).filter(
        DailyNote.user_id == user_id,
        DailyNote.note_date == entry_date
    ).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No journal entry found for date {entry_date}"
        )

    db.delete(entry)
    db.commit()

    return None
