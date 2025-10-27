"""
Service functions for water tracking.
"""
from datetime import date, datetime
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session

from ..models.water_tracking import DailyWaterGoal, WaterIntakeEntry


def set_user_daily_water_goal(db: Session, user_id: int, goal_ml: int) -> DailyWaterGoal:
    existing = db.query(DailyWaterGoal).filter(DailyWaterGoal.user_id == user_id).first()
    if existing:
        existing.goal_ml = goal_ml
        existing.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    water_goal = DailyWaterGoal(user_id=user_id, goal_ml=goal_ml)
    db.add(water_goal)
    db.commit()
    db.refresh(water_goal)
    return water_goal


def log_user_water_intake(db: Session, user_id: int, volume_ml: int, entry_date: Optional[date] = None) -> WaterIntakeEntry:
    if entry_date is None:
        entry_date = date.today()
    entry = WaterIntakeEntry(user_id=user_id, volume_ml=volume_ml, entry_date=entry_date)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_daily_water_summary_data(
    db: Session,
    user_id: int,
    target_date: Optional[date] = None
) -> Tuple[Optional[int], int, List[WaterIntakeEntry], float, int, bool, Optional[int]]:
    if target_date is None:
        target_date = date.today()

    goal_row = db.query(DailyWaterGoal).filter(DailyWaterGoal.user_id == user_id).first()
    goal_ml = goal_row.goal_ml if goal_row else None

    entries = (
        db.query(WaterIntakeEntry)
        .filter(WaterIntakeEntry.user_id == user_id, WaterIntakeEntry.entry_date == target_date)
        .order_by(WaterIntakeEntry.created_at.desc())
        .all()
    )
    total_ml = sum(e.volume_ml for e in entries)

    if goal_ml and goal_ml > 0:
        pct = min(100.0, round((total_ml / goal_ml) * 100, 2))
        remaining = max(0, goal_ml - total_ml)
        exceeded = total_ml >= goal_ml
        over_ml = total_ml - goal_ml if exceeded else None
    else:
        pct = 0.0
        remaining = 0
        exceeded = False
        over_ml = None

    return goal_ml, total_ml, entries, pct, remaining, exceeded, over_ml


def get_user_water_goal(db: Session, user_id: int) -> Optional[DailyWaterGoal]:
    return db.query(DailyWaterGoal).filter(DailyWaterGoal.user_id == user_id).first()


