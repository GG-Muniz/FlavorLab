#!/usr/bin/env python3
"""
Multi-Provider LLM Comparison Test
Compares Claude 3.5 Haiku vs OpenAI GPT-4o-mini vs GPT-4o for meal plan generation
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


async def run_provider_comparison():
    """Run comprehensive comparison across providers"""

    print("\n" + "="*80)
    print("  MULTI-PROVIDER LLM COMPARISON TEST")
    print("  Testing: Claude 3.5 Haiku | GPT-4o-mini | GPT-4o")
    print("="*80)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Test configurations
    providers = [
        {
            "name": "Claude 3.5 Haiku",
            "provider": "anthropic",
            "model": "claude-3-5-haiku-20241022"
        },
        {
            "name": "GPT-4o-mini",
            "provider": "openai",
            "model": "gpt-4o-mini"
        },
        {
            "name": "GPT-4o",
            "provider": "openai",
            "model": "gpt-4o"
        }
    ]

    # Test scenarios (3 scenarios to keep test time reasonable)
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
        }
    ]

    all_results = {}

    # Test each provider
    for provider_config in providers:
        provider_name = provider_config["name"]
        print(f"\n{'='*80}")
        print(f"  TESTING: {provider_name}")
        print(f"  Provider: {provider_config['provider']} | Model: {provider_config['model']}")
        print(f"{'='*80}\n")

        provider_results = []

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
                    db=db,
                    provider=provider_config['provider'],
                    model=provider_config['model']
                )

                elapsed_ms = (time.time() - start) * 1000
                db.close()

                # Check quality
                has_description = meal_plans[0].meals[0].description is not None
                has_tags = meal_plans[0].meals[0].tags is not None and len(meal_plans[0].meals[0].tags) > 0
                num_meals = len(meal_plans[0].meals)

                # Check constraint adherence in tags
                expected_tags = scenario['config']['diet'] + scenario['config'].get('allergies', [])
                actual_tags = [tag.lower() for meal in meal_plans[0].meals for tag in (meal.tags or [])]
                constraint_adherence = sum(1 for exp in expected_tags if any(exp.lower() in tag for tag in actual_tags))

                print(f"  ✅ Success: {format_time(elapsed_ms)}")
                print(f"     Meals: {num_meals} | Description: {has_description} | Tags: {has_tags} | Constraints: {constraint_adherence}/{len(expected_tags)}")

                provider_results.append({
                    "scenario": scenario['name'],
                    "time_ms": elapsed_ms,
                    "success": True,
                    "meals": num_meals,
                    "has_description": has_description,
                    "has_tags": has_tags,
                    "constraint_score": constraint_adherence / len(expected_tags) if expected_tags else 1.0
                })

            except Exception as e:
                elapsed_ms = (time.time() - start) * 1000 if 'start' in locals() else 0
                print(f"  ❌ Failed: {format_time(elapsed_ms) if elapsed_ms else 'N/A'}")
                print(f"     Error: {str(e)[:80]}...")

                provider_results.append({
                    "scenario": scenario['name'],
                    "time_ms": elapsed_ms,
                    "success": False,
                    "error": str(e)[:100]
                })

                # Close DB if open
                if 'db' in locals():
                    db.close()

            # Small delay between requests
            if i < len(scenarios):
                await asyncio.sleep(1)
            print()

        all_results[provider_name] = provider_results

        # Small delay between providers
        await asyncio.sleep(2)

    # Generate comprehensive comparison report
    print("\n" + "="*80)
    print("  COMPREHENSIVE COMPARISON REPORT")
    print("="*80)

    # Overall statistics
    print("\n📊 OVERALL STATISTICS:")
    print(f"   {'Provider':<20} {'Success Rate':<15} {'Avg Speed':<12} {'Quality Score'}")
    print(f"   {'-'*20} {'-'*15} {'-'*12} {'-'*15}")

    provider_summary = {}

    for provider_name, results in all_results.items():
        successful = [r for r in results if r.get('success')]
        total = len(results)
        success_rate = (len(successful) / total * 100) if total > 0 else 0

        if successful:
            avg_time = sum(r['time_ms'] for r in successful) / len(successful)
            quality_score = (
                sum(r.get('has_description', 0) for r in successful) / len(successful) * 50 +
                sum(r.get('has_tags', 0) for r in successful) / len(successful) * 50
            )
            avg_constraint = sum(r.get('constraint_score', 0) for r in successful) / len(successful) * 100

            provider_summary[provider_name] = {
                "success_rate": success_rate,
                "avg_time": avg_time,
                "quality_score": quality_score,
                "constraint_score": avg_constraint
            }

            print(f"   {provider_name:<20} {success_rate:>6.0f}% ({len(successful)}/{total})"
                  f"   {format_time(avg_time):<12} {quality_score:>5.0f}% ({avg_constraint:.0f}% constraints)")
        else:
            print(f"   {provider_name:<20} {'0% (0/' + str(total) + ')':<15} {'N/A':<12} {'N/A'}")

    # Speed comparison
    print("\n⚡ SPEED COMPARISON (with recipes):")
    print(f"   {'Provider':<20} {'Avg Time':<12} {'Min Time':<12} {'Max Time'}")
    print(f"   {'-'*20} {'-'*12} {'-'*12} {'-'*12}")

    for provider_name, results in all_results.items():
        successful_with_recipes = [r for r in results if r.get('success') and 'WITH recipes' in r['scenario']]
        if successful_with_recipes:
            times = [r['time_ms'] for r in successful_with_recipes]
            avg = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            print(f"   {provider_name:<20} {format_time(avg):<12} {format_time(min_time):<12} {format_time(max_time)}")

    # Speed comparison without recipes
    print("\n⚡ SPEED COMPARISON (without recipes):")
    print(f"   {'Provider':<20} {'Avg Time':<12} {'Speedup vs With Recipes'}")
    print(f"   {'-'*20} {'-'*12} {'-'*25}")

    for provider_name, results in all_results.items():
        successful_without = [r for r in results if r.get('success') and 'WITHOUT recipes' in r['scenario']]
        successful_with = [r for r in results if r.get('success') and 'WITH recipes' in r['scenario']]

        if successful_without:
            avg_without = sum(r['time_ms'] for r in successful_without) / len(successful_without)

            if successful_with:
                avg_with = sum(r['time_ms'] for r in successful_with) / len(successful_with)
                speedup = avg_with / avg_without
                print(f"   {provider_name:<20} {format_time(avg_without):<12} {speedup:.1f}x faster")
            else:
                print(f"   {provider_name:<20} {format_time(avg_without):<12} N/A")

    # Detailed results table
    print("\n📋 DETAILED RESULTS:")
    print(f"   {'Scenario':<40} {'Provider':<20} {'Time':<12} {'Status'}")
    print(f"   {'-'*40} {'-'*20} {'-'*12} {'-'*10}")

    for scenario in scenarios:
        for provider_name, results in all_results.items():
            result = next((r for r in results if r['scenario'] == scenario['name']), None)
            if result:
                status = "✅ Success" if result.get('success') else "❌ Failed"
                time_str = format_time(result['time_ms']) if result['time_ms'] > 0 else "N/A"
                print(f"   {scenario['name']:<40} {provider_name:<20} {time_str:<12} {status}")

    # Winner determination
    print("\n" + "="*80)
    print("🏆 RECOMMENDATIONS:")
    print("="*80)

    if provider_summary:
        # Find fastest provider
        fastest = min(provider_summary.items(), key=lambda x: x[1]['avg_time'])
        print(f"\n⚡ FASTEST: {fastest[0]}")
        print(f"   Average response time: {format_time(fastest[1]['avg_time'])}")

        # Find highest quality
        highest_quality = max(provider_summary.items(), key=lambda x: x[1]['quality_score'])
        print(f"\n✅ HIGHEST QUALITY: {highest_quality[0]}")
        print(f"   Quality score: {highest_quality[1]['quality_score']:.0f}%")
        print(f"   Constraint adherence: {highest_quality[1]['constraint_score']:.0f}%")

        # Best constraint adherence
        best_constraints = max(provider_summary.items(), key=lambda x: x[1]['constraint_score'])
        print(f"\n🎯 BEST CONSTRAINT ADHERENCE: {best_constraints[0]}")
        print(f"   Constraint score: {best_constraints[1]['constraint_score']:.0f}%")

    print("\n" + "="*80)
    print("💡 NOTES:")
    print("   • Speed measured for single-day meal plans")
    print("   • Quality = Field completeness (description + tags)")
    print("   • Constraint adherence = % of dietary restrictions/allergies in tags")
    print("   • Cost considerations: GPT-4o-mini is typically cheaper than Haiku/GPT-4o")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_provider_comparison())
