"""
Test script for LLM meal plan generation.

This script demonstrates the LLM-powered meal plan generator with sample data.
"""
import asyncio
import json
from app.services.llm_service import generate_llm_meal_plan
from app.models.user import User


async def test_llm_meal_plan():
    """Test the LLM meal plan generation with sample survey data."""

    # Create a mock user with survey data
    mock_user = User(
        id=999,
        email="test@example.com",
        username="testuser",
        hashed_password="fake_hash",
        preferences={
            "survey_data": {
                "healthPillars": ["Increased Energy", "Heart Health"],
                "dietaryRestrictions": ["vegetarian"],
                "mealComplexity": "moderate",
                "dislikedIngredients": ["mushrooms", "olives"],
                "mealsPerDay": "3-meals-2-snacks",
                "allergies": ["peanuts"],
                "primaryGoal": "Lose weight and increase energy levels"
            },
            "health_goals": [1, 4]
        }
    )

    print("=" * 80)
    print("TEST 1: Basic Meal Plan (without recipes)")
    print("=" * 80)
    print("\nUser Survey Data:")
    print(json.dumps(mock_user.preferences["survey_data"], indent=2))
    print("\n" + "-" * 80)
    print("Generating meal plan...\n")

    try:
        # Test without recipes
        meal_plans = await generate_llm_meal_plan(
            user=mock_user,
            num_days=1,
            include_recipes=False
        )

        print("✅ SUCCESS! Generated meal plan:\n")
        for day_plan in meal_plans:
            print(f"Day: {day_plan.day}")
            print(f"Total meals: {len(day_plan.meals)}")
            print()
            for meal in day_plan.meals:
                print(f"  {meal.type.upper()}: {meal.name}")
                print(f"    Calories: {meal.calories}")
                print(f"    Description: {meal.description}")
                print()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("TEST 2: Detailed Meal Plan (with full recipes)")
    print("=" * 80)
    print("\nGenerating meal plan with recipes...\n")

    try:
        # Test with recipes
        meal_plans_detailed = await generate_llm_meal_plan(
            user=mock_user,
            num_days=1,
            include_recipes=True
        )

        print("✅ SUCCESS! Generated detailed meal plan:\n")
        for day_plan in meal_plans_detailed:
            print(f"Day: {day_plan.day}")
            print(f"Total meals: {len(day_plan.meals)}")
            print()
            for i, meal in enumerate(day_plan.meals, 1):
                print(f"  MEAL {i}: {meal.name}")
                print(f"  Type: {meal.type}")
                print(f"  Calories: {meal.calories}")
                print(f"  Description: {meal.description}")

                if meal.ingredients:
                    print(f"\n  Ingredients ({len(meal.ingredients)}):")
                    for ing in meal.ingredients[:5]:  # Show first 5
                        print(f"    • {ing}")
                    if len(meal.ingredients) > 5:
                        print(f"    ... and {len(meal.ingredients) - 5} more")

                if meal.servings:
                    print(f"\n  Servings: {meal.servings}")

                if meal.prep_time_minutes:
                    print(f"  Prep time: {meal.prep_time_minutes} minutes")

                if meal.cook_time_minutes:
                    print(f"  Cook time: {meal.cook_time_minutes} minutes")

                if meal.instructions:
                    print(f"\n  Instructions ({len(meal.instructions)} steps):")
                    for j, step in enumerate(meal.instructions[:3], 1):  # Show first 3
                        print(f"    {j}. {step}")
                    if len(meal.instructions) > 3:
                        print(f"    ... and {len(meal.instructions) - 3} more steps")

                if meal.nutrition:
                    print(f"\n  Nutrition:")
                    for key, value in list(meal.nutrition.items())[:5]:
                        print(f"    {key}: {value}")

                print("\n" + "-" * 80)

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("Testing complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_llm_meal_plan())
