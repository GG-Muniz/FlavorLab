"""
Pydantic schemas for journal/daily notes API.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class JournalEntryCreate(BaseModel):
    """Request schema for creating/updating a journal entry."""
    note_text: str = Field(..., min_length=1, description="Journal note text")


class JournalEntryUpdate(BaseModel):
    """Request schema for updating a journal entry."""
    note_text: Optional[str] = Field(None, description="Updated journal note text")


class JournalEntryResponse(BaseModel):
    """Response schema for a journal entry."""
    id: int
    user_id: int
    note_date: date
    note_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
