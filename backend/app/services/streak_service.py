from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.meal import Meal

def calculate_current_streak(db: Session, user_id: int) -> int:
    """
    Calculate user's current meal logging streak.
    
    Counts consecutive days (including today) where user logged at least one meal.
    Returns 0 if no meals logged or streak is broken.
    """
    today = date.today()
    streak = 0
    check_date = today
    
    # Count backwards until we find a day with no meals
    while True:
        # Check if user has any meals logged on check_date
        has_meal = db.query(Meal).filter(
            Meal.user_id == user_id,
            func.date(Meal.date_logged) == check_date
        ).first() is not None
        
        if not has_meal:
            break
            
        streak += 1
        check_date -= timedelta(days=1)
        
        # Safety limit: don't go back more than 365 days
        if streak >= 365:
            break
    
    return streak
