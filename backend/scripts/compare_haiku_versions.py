#!/usr/bin/env python3
"""
Claude Haiku 3.0 vs 3.5 Comparison Test
Tests the new 3.5 Haiku model for speed and reliability improvements
"""

import asyncio
import time
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.llm_service import generate_llm_meal_plan
from app.models.user import User
from app.database import SessionLocal


def format_time(ms):
    """Format milliseconds nicely"""
    if ms < 1000:
        return f"{ms:.0f}ms"
    else:
        return f"{ms/1000:.1f}s"


async def run_comparison_tests():
    """Run comprehensive comparison between 3.0 and 3.5"""

    print("\n" + "="*70)
    print("  CLAUDE 3.5 HAIKU PERFORMANCE TEST")
    print("  Upgraded from: claude-3-haiku-20240307")
    print("  New model: claude-3-5-haiku-20241022")
    print("="*70)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Test scenarios
    scenarios = [
        {
            "name": "Simple Paleo (WITH recipes)",
            "config": {
                "diet": ["paleo"],
                "allergies": [],
                "health_goals": [1, 2],
                "include_recipes": True
            }
        },
        {
            "name": "Simple Paleo (WITHOUT recipes)",
            "config": {
                "diet": ["paleo"],
                "allergies": [],
                "health_goals": [1, 2],
                "include_recipes": False
            }
        },
        {
            "name": "Complex Pescatarian (3 allergies)",
            "config": {
                "diet": ["pescatarian"],
                "allergies": ["Shellfish", "Soy", "Gluten"],
                "health_goals": [3, 5, 6],
                "include_recipes": True
            }
        },
        {
            "name": "Keto (2 allergies + dislikes)",
            "config": {
                "diet": ["keto"],
                "allergies": ["Peanuts", "Dairy"],
                "disliked": ["mushrooms", "onions"],
                "health_goals": [1, 7],
                "include_recipes": True
            }
        },
        {
            "name": "Vegetarian (Complex)",
            "config": {
                "diet": ["vegetarian"],
                "allergies": ["Soy", "Gluten"],
                "disliked": ["tomatoes"],
                "health_goals": [1, 4, 8],
                "include_recipes": True
            }
        }
    ]

    results = []
    total_time = 0

    for i, scenario in enumerate(scenarios, 1):
        print(f"[Test {i}/{len(scenarios)}] {scenario['name']}")
        print(f"  Config: {scenario['config']['diet']}, " +
              f"Allergies: {len(scenario['config'].get('allergies', []))}, " +
              f"Recipes: {scenario['config']['include_recipes']}")

        # Create test user
        user = User(
            id=999,
            email="test@test.com",
            username="test",
            preferences={
                "health_goals": scenario['config']['health_goals'],
                "survey_data": {
                    "healthPillars": ["Increased Energy", "Improved Digestion"],
                    "dietaryRestrictions": scenario['config']['diet'],
                    "mealComplexity": "moderate",
                    "dislikedIngredients": scenario['config'].get('disliked', []),
                    "mealsPerDay": "3-meals-2-snacks",
                    "allergies": scenario['config'].get('allergies', []),
                    "primaryGoal": "General wellness"
                }
            }
        )

        try:
            db = SessionLocal()
            start = time.time()

            meal_plans = await generate_llm_meal_plan(
                user=user,
                num_days=1,
                include_recipes=scenario['config']['include_recipes'],
                db=db
            )

            elapsed_ms = (time.time() - start) * 1000
            db.close()

            # Check quality
            has_description = meal_plans[0].meals[0].description is not None
            has_tags = meal_plans[0].meals[0].tags is not None and len(meal_plans[0].meals[0].tags) > 0
            num_meals = len(meal_plans[0].meals)

            print(f"  ✅ Success: {format_time(elapsed_ms)}")
            print(f"     Meals: {num_meals} | Has description: {has_description} | Has tags: {has_tags}")

            results.append({
                "name": scenario['name'],
                "time_ms": elapsed_ms,
                "success": True,
                "meals": num_meals,
                "has_description": has_description,
                "has_tags": has_tags
            })

            total_time += elapsed_ms

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            print(f"  ❌ Failed: {format_time(elapsed_ms)}")
            print(f"     Error: {str(e)[:80]}...")

            results.append({
                "name": scenario['name'],
                "time_ms": elapsed_ms,
                "success": False,
                "error": str(e)[:100]
            })

        # Small delay between requests
        if i < len(scenarios):
            await asyncio.sleep(1)
        print()

    # Generate comprehensive report
    print("="*70)
    print("  RESULTS SUMMARY - CLAUDE 3.5 HAIKU")
    print("="*70)

    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    print(f"\n📊 Overall Performance:")
    print(f"   Total tests: {len(results)}")
    print(f"   Successful: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.0f}%)")
    print(f"   Failed: {len(failed)}/{len(results)}")

    if successful:
        times = [r['time_ms'] for r in successful]
        with_recipes = [r for r in successful if 'WITH recipes' in r['name']]
        without_recipes = [r for r in successful if 'WITHOUT recipes' in r['name']]

        print(f"\n⚡ Speed Metrics:")
        print(f"   Average: {format_time(sum(times)/len(times))}")
        print(f"   Fastest: {format_time(min(times))}")
        print(f"   Slowest: {format_time(max(times))}")

        if with_recipes:
            avg_with = sum(r['time_ms'] for r in with_recipes) / len(with_recipes)
            print(f"   Avg WITH recipes: {format_time(avg_with)}")

        if without_recipes:
            avg_without = sum(r['time_ms'] for r in without_recipes) / len(without_recipes)
            print(f"   Avg WITHOUT recipes: {format_time(avg_without)}")

            if with_recipes:
                speedup = avg_with / avg_without
                print(f"   Speedup (no recipes): {speedup:.1f}x faster")

        print(f"\n✅ Quality Metrics:")
        with_desc = len([r for r in successful if r.get('has_description')])
        with_tags = len([r for r in successful if r.get('has_tags')])
        print(f"   Includes description: {with_desc}/{len(successful)} ({with_desc/len(successful)*100:.0f}%)")
        print(f"   Includes tags: {with_tags}/{len(successful)} ({with_tags/len(successful)*100:.0f}%)")

        print(f"\n📋 Detailed Results:")
        print(f"   {'Scenario':<40} {'Time':<12} {'Status'}")
        print(f"   {'-'*40} {'-'*12} {'-'*10}")
        for r in results:
            status = "✅ Success" if r.get('success') else "❌ Failed"
            print(f"   {r['name']:<40} {format_time(r['time_ms']):<12} {status}")

    print("\n" + "="*70)
    print("📈 EXPECTED IMPROVEMENTS OVER HAIKU 3.0:")
    print("   • Speed: 3-4x faster (16s → 5-6s with recipes)")
    print("   • Reliability: Better field completeness")
    print("   • Quality: More consistent JSON formatting")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(run_comparison_tests())
