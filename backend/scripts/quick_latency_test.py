#!/usr/bin/env python3
"""
Quick LLM Latency Test - Fast response time testing
"""

import asyncio
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.llm_service import generate_llm_meal_plan, LLMResponseError
from app.models.user import User
from app.database import SessionLocal


async def quick_test():
    """Quick test with 3 scenarios"""

    print("\n" + "="*60)
    print("QUICK LLM LATENCY TEST")
    print("="*60)

    # Test user
    user = User(
        id=999,
        email="test@test.com",
        username="test",
        preferences={
            "health_goals": [1, 6, 2],
            "survey_data": {
                "healthPillars": ["Increased Energy", "Heart Health", "Improved Digestion"],
                "dietaryRestrictions": ["paleo"],
                "mealComplexity": "moderate",
                "dislikedIngredients": ["tomatoes"],
                "mealsPerDay": "3-meals-2-snacks",
                "allergies": ["Peanuts", "Eggs"],
                "primaryGoal": "General wellness"
            }
        }
    )

    results = []

    # Test 1: With recipes
    print("\n[Test 1/3] Paleo diet WITH recipes...")
    try:
        db = SessionLocal()
        start = time.time()
        meal_plans = await generate_llm_meal_plan(user=user, num_days=1, include_recipes=True, db=db)
        elapsed = (time.time() - start) * 1000
        db.close()

        print(f"  ✅ Success: {elapsed:.0f}ms")
        print(f"  📊 Meals generated: {len(meal_plans[0].meals)}")
        results.append(("With recipes", elapsed, True))
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        print(f"  ❌ Failed: {elapsed:.0f}ms")
        print(f"  Error: {str(e)[:100]}")
        results.append(("With recipes", elapsed, False))

    await asyncio.sleep(2)

    # Test 2: Without recipes (faster)
    print("\n[Test 2/3] Paleo diet WITHOUT recipes...")
    try:
        db = SessionLocal()
        start = time.time()
        meal_plans = await generate_llm_meal_plan(user=user, num_days=1, include_recipes=False, db=db)
        elapsed = (time.time() - start) * 1000
        db.close()

        print(f"  ✅ Success: {elapsed:.0f}ms")
        print(f"  📊 Meals generated: {len(meal_plans[0].meals)}")
        results.append(("Without recipes", elapsed, True))
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        print(f"  ❌ Failed: {elapsed:.0f}ms")
        print(f"  Error: {str(e)[:100]}")
        results.append(("Without recipes", elapsed, False))

    await asyncio.sleep(2)

    # Test 3: Complex dietary restrictions
    print("\n[Test 3/3] Complex restrictions (pescatarian + 3 allergies)...")
    user.preferences["survey_data"]["dietaryRestrictions"] = ["pescatarian"]
    user.preferences["survey_data"]["allergies"] = ["Shellfish", "Soy", "Gluten"]

    try:
        db = SessionLocal()
        start = time.time()
        meal_plans = await generate_llm_meal_plan(user=user, num_days=1, include_recipes=True, db=db)
        elapsed = (time.time() - start) * 1000
        db.close()

        print(f"  ✅ Success: {elapsed:.0f}ms")
        print(f"  📊 Meals generated: {len(meal_plans[0].meals)}")
        results.append(("Complex restrictions", elapsed, True))
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        print(f"  ❌ Failed: {elapsed:.0f}ms")
        print(f"  Error: {str(e)[:100]}")
        results.append(("Complex restrictions", elapsed, False))

    # Summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)

    successful = [r for r in results if r[2]]

    print(f"\nTotal Tests: {len(results)}")
    print(f"Successful: {len(successful)}/{len(results)}")

    if successful:
        times = [r[1] for r in successful]
        print(f"\nResponse Times (Successful):")
        print(f"  Average: {sum(times)/len(times):.0f}ms")
        print(f"  Fastest: {min(times):.0f}ms")
        print(f"  Slowest: {max(times):.0f}ms")

        print(f"\nDetailed Timings:")
        for name, elapsed, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {name}: {elapsed:.0f}ms")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(quick_test())
