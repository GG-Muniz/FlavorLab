#!/usr/bin/env python3
import asyncio
import time
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.services.llm_service import generate_llm_meal_plan
from app.models.user import User
from app.database import SessionLocal

async def quick_test():
    user = User(
        id=999,
        email="test@test.com",
        username="test",
        preferences={
            "health_goals": [1, 2],
            "survey_data": {
                "healthPillars": ["Increased Energy"],
                "dietaryRestrictions": ["paleo"],
                "mealComplexity": "moderate",
                "dislikedIngredients": [],
                "mealsPerDay": "3-meals-2-snacks",
                "allergies": [],
                "primaryGoal": "General wellness"
            }
        }
    )
    
    print("Testing gpt-4o-mini latency (3 iterations)...\n")
    
    times = []
    for i in range(3):
        db = SessionLocal()
        print(f"Test {i+1}/3... ", end="", flush=True)
        start = time.time()
        
        try:
            await generate_llm_meal_plan(user=user, num_days=1, include_recipes=True, db=db)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            print(f"✅ {elapsed:.0f}ms")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            db.close()
        
        if i < 2:
            await asyncio.sleep(1)
    
    if times:
        print(f"\n📊 Results:")
        print(f"   Average: {sum(times)/len(times):.0f}ms")
        print(f"   Min: {min(times):.0f}ms")
        print(f"   Max: {max(times):.0f}ms")

asyncio.run(quick_test())
