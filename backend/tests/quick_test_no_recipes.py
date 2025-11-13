#!/usr/bin/env python3
import asyncio, time, sys, os
sys.path.insert(0, os.path.abspath('.'))
from app.services.llm_service import generate_llm_meal_plan
from app.models.user import User
from app.database import SessionLocal

async def test():
    user = User(id=999, email="test@test.com", username="test", preferences={"health_goals": [1], "survey_data": {"healthPillars": ["Energy"], "dietaryRestrictions": ["paleo"], "mealComplexity": "moderate", "dislikedIngredients": [], "mealsPerDay": "3-meals", "allergies": [], "primaryGoal": "wellness"}})
    
    print("Testing Claude Haiku WITHOUT recipes (3 tests)...\n")
    times = []
    for i in range(3):
        db = SessionLocal()
        print(f"Test {i+1}/3... ", end="", flush=True)
        start = time.time()
        try:
            await generate_llm_meal_plan(user=user, num_days=1, include_recipes=False, db=db)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            print(f"✅ {elapsed:.0f}ms")
        except Exception as e:
            print(f"❌ {e}")
        finally:
            db.close()
        if i < 2:
            await asyncio.sleep(1)
    
    if times:
        print(f"\n📊 Average: {sum(times)/len(times):.0f}ms (Min: {min(times):.0f}ms, Max: {max(times):.0f}ms)")

asyncio.run(test())
