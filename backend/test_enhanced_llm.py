"""
Comprehensive test for enhanced LLM meal plan generation.

Tests:
1. Allergy safety with derivatives (soy allergy should avoid edamame, tofu, etc.)
2. Meal structure enforcement (3 meals, 3 meals + 2 snacks, etc.)
3. Detailed recipe generation with include_recipes=True
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"


def get_auth_token():
    """Get authentication token."""
    login_data = {
        "email": "testnutrition@example.com",
        "password": "TestPassword123"
    }
    response = requests.post(f"{BASE_URL}/users/login", json=login_data)
    return response.json()["access_token"]


def test_allergy_safety():
    """Test 1: Allergy safety with derivative awareness."""
    print("=" * 80)
    print("TEST 1: ALLERGY SAFETY - Soy Allergy (No edamame, tofu, soy sauce, etc.)")
    print("=" * 80)

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Submit survey with soy allergy
    survey_data = {
        "healthPillars": ["Muscle Recovery", "Increased Energy"],
        "dietaryRestrictions": ["vegan"],
        "mealComplexity": "moderate",
        "dislikedIngredients": [],
        "mealsPerDay": "3",
        "allergies": ["soy"],  # CRITICAL: Should avoid ALL soy derivatives
        "primaryGoal": "build muscle on plant-based diet"
    }

    requests.post(f"{BASE_URL}/users/me/survey", json=survey_data, headers=headers)

    # Generate meal plan
    print("\n⏳ Generating meal plan for user with SOY ALLERGY...")
    print("   Checking for: tofu, edamame, soy sauce, soy milk, tempeh, miso")

    response = requests.post(
        f"{BASE_URL}/users/me/llm-meal-plan",
        json={"num_days": 2},
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()

        # Check for soy derivatives
        soy_derivatives = ['tofu', 'edamame', 'soy sauce', 'soy milk', 'tempeh', 'miso', 'soy']
        violations = []

        for day in result['plan']:
            for meal in day['meals']:
                meal_text = f"{meal['name']} {meal['description']}".lower()
                for derivative in soy_derivatives:
                    if derivative in meal_text:
                        violations.append(f"❌ VIOLATION: {derivative} found in {meal['name']}")

        if violations:
            print("\n🚨 ALLERGY SAFETY VIOLATIONS DETECTED:")
            for v in violations:
                print(f"  {v}")
        else:
            print("\n✅ PASS: No soy derivatives detected in meal plan!")

        print(f"\n📋 Generated {len(result['plan'])} days:")
        for day in result['plan']:
            print(f"\n{day['day']}:")
            for meal in day['meals']:
                print(f"  • {meal['name']}")
    else:
        print(f"\n❌ Failed: {response.status_code}")


def test_meal_structure():
    """Test 2: Meal structure enforcement."""
    print("\n" + "=" * 80)
    print("TEST 2: MEAL STRUCTURE - 3 Meals + 2 Snacks (5 items per day)")
    print("=" * 80)

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Submit survey with specific meal structure
    survey_data = {
        "healthPillars": ["Better Sleep", "Increased Energy"],
        "dietaryRestrictions": ["vegetarian"],
        "mealComplexity": "simple",
        "dislikedIngredients": ["mushrooms"],
        "mealsPerDay": "3-meals-2-snacks",  # CRITICAL: Should generate 5 items per day
        "allergies": [],
        "primaryGoal": "maintain steady energy throughout the day"
    }

    requests.post(f"{BASE_URL}/users/me/survey", json=survey_data, headers=headers)

    # Generate meal plan
    print("\n⏳ Generating meal plan with 3 MEALS + 2 SNACKS structure...")

    response = requests.post(
        f"{BASE_URL}/users/me/llm-meal-plan",
        json={"num_days": 2},
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()

        print(f"\n📋 Validating meal structure:")
        all_correct = True

        for day in result['plan']:
            meal_count = len(day['meals'])
            snack_count = sum(1 for m in day['meals'] if m['type'].lower() == 'snack')
            meal_types = [m['type'] for m in day['meals']]

            print(f"\n{day['day']}:")
            print(f"  Total items: {meal_count} (expected: 5)")
            print(f"  Snacks: {snack_count} (expected: 2)")
            print(f"  Types: {', '.join(meal_types)}")

            if meal_count != 5:
                print(f"  ❌ FAIL: Expected 5 items, got {meal_count}")
                all_correct = False
            elif snack_count != 2:
                print(f"  ⚠️  WARNING: Expected 2 snacks, got {snack_count}")
            else:
                print(f"  ✅ PASS: Correct structure!")

            # Show meals
            for meal in day['meals']:
                emoji = "🍽️" if meal['type'] != 'snack' else "🍎"
                print(f"    {emoji} {meal['type']}: {meal['name']} ({meal['calories']} kcal)")

        if all_correct:
            print("\n✅ OVERALL PASS: Meal structure enforced correctly!")
        else:
            print("\n❌ OVERALL FAIL: Meal structure not followed")
    else:
        print(f"\n❌ Failed: {response.status_code}")


def test_detailed_recipes():
    """Test 3: Detailed recipe generation."""
    print("\n" + "=" * 80)
    print("TEST 3: DETAILED RECIPES - With ingredients, instructions, nutrition")
    print("=" * 80)

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Submit simple survey
    survey_data = {
        "healthPillars": ["Heart Health"],
        "dietaryRestrictions": [],
        "mealComplexity": "moderate",
        "dislikedIngredients": [],
        "mealsPerDay": "3",
        "allergies": [],
        "primaryGoal": "improve cardiovascular health"
    }

    requests.post(f"{BASE_URL}/users/me/survey", json=survey_data, headers=headers)

    # Generate meal plan WITH RECIPES
    print("\n⏳ Generating detailed meal plan with FULL RECIPES...")
    print("   (This may take longer due to additional content generation)")

    response = requests.post(
        f"{BASE_URL}/users/me/llm-meal-plan?include_recipes=true",
        json={"num_days": 1},
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()

        print(f"\n✨ DETAILED RECIPE OUTPUT:")
        print("=" * 80)

        for day in result['plan']:
            print(f"\n📆 {day['day']}")

            for meal in day['meals']:
                print(f"\n{'─' * 80}")
                print(f"🍽️  {meal['type'].upper()}: {meal['name']}")
                print(f"📊 {meal['calories']} calories")
                print(f"📝 {meal['description']}")

                # Check for detailed recipe fields
                has_ingredients = meal.get('ingredients') is not None
                has_instructions = meal.get('instructions') is not None
                has_nutrition = meal.get('nutrition') is not None
                has_servings = meal.get('servings') is not None
                has_times = meal.get('prep_time_minutes') is not None

                if has_ingredients:
                    print(f"\n📦 INGREDIENTS:")
                    for ingredient in meal['ingredients']:
                        print(f"   • {ingredient}")
                else:
                    print(f"\n❌ MISSING: ingredients")

                if has_servings:
                    print(f"\n👥 Servings: {meal['servings']}")
                if has_times:
                    print(f"⏱️  Prep: {meal.get('prep_time_minutes', 0)} min | Cook: {meal.get('cook_time_minutes', 0)} min")

                if has_instructions:
                    print(f"\n📋 INSTRUCTIONS:")
                    for i, step in enumerate(meal['instructions'], 1):
                        print(f"   {i}. {step}")
                else:
                    print(f"\n❌ MISSING: instructions")

                if has_nutrition:
                    print(f"\n💪 NUTRITION:")
                    for key, value in meal['nutrition'].items():
                        print(f"   {key.capitalize()}: {value}")
                else:
                    print(f"\n❌ MISSING: nutrition")

                # Summary
                recipe_complete = all([has_ingredients, has_instructions, has_nutrition, has_servings])
                if recipe_complete:
                    print(f"\n✅ Complete detailed recipe provided!")
                else:
                    missing = []
                    if not has_ingredients: missing.append("ingredients")
                    if not has_instructions: missing.append("instructions")
                    if not has_nutrition: missing.append("nutrition")
                    if not has_servings: missing.append("servings")
                    print(f"\n⚠️  Incomplete recipe. Missing: {', '.join(missing)}")

        print("\n" + "=" * 80)
    else:
        print(f"\n❌ Failed: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("\n🧪 ENHANCED LLM MEAL PLAN GENERATION - COMPREHENSIVE TESTS\n")

    test_allergy_safety()
    print("\n")

    test_meal_structure()
    print("\n")

    test_detailed_recipes()

    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
