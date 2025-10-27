"""
Pydantic schemas for water (hydration) tracking.
"""
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DailyWaterGoalSet(BaseModel):
    goal_ml: int = Field(..., ge=0, description="Daily water goal in milliliters")


class UserWaterGoalResponse(BaseModel):
    goal_ml: int
    last_updated: datetime
    message: str


class WaterIntakeLog(BaseModel):
    volume_ml: int = Field(..., ge=1, description="Water volume in milliliters")


class WaterIntakeEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    volume_ml: int
    created_at: datetime
    entry_date: date


class DailyWaterSummaryResponse(BaseModel):
    goal_ml: Optional[int]
    total_intake_ml: int
    percentage: float
    remaining_ml: int
    goal_exceeded: bool
    excess_ml: Optional[int]
    entries: List[WaterIntakeEntryResponse] = []
    entry_date: date


