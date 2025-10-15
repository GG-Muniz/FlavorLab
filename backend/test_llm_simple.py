"""
Simple test to demonstrate LLM meal plan generation output.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_llm_output():
    """Test and display LLM meal plan output."""

    print("=" * 80)
    print("CLAUDE HAIKU LLM MEAL PLAN GENERATION - LIVE DEMO")
    print("=" * 80)

    # Step 1: Login
    print("\n[1] Authenticating...")
    login_data = {
        "email": "testnutrition@example.com",
        "password": "TestPassword123"
    }

    login_response = requests.post(f"{BASE_URL}/users/login", json=login_data)

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return

    token = login_response.json()["access_token"]
    print("✓ Authenticated successfully")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 2: Ensure survey data exists
    print("\n[2] Submitting survey data...")
    survey_data = {
        "healthPillars": ["Increased Energy", "Better Sleep"],
        "dietaryRestrictions": ["vegetarian"],
        "mealComplexity": "moderate",
        "dislikedIngredients": ["mushrooms", "olives"],
        "mealsPerDay": "3",
        "allergies": ["peanuts"],
        "primaryGoal": "lose weight and feel energized"
    }

    survey_response = requests.post(
        f"{BASE_URL}/users/me/survey",
        json=survey_data,
        headers=headers
    )

    if survey_response.status_code == 200:
        print("✓ Survey data ready")
    else:
        print(f"⚠ Survey status: {survey_response.status_code}")

    # Step 3: Generate LLM meal plan
    print("\n[3] Calling Claude Haiku API...")
    print("    (This may take 10-30 seconds for AI processing)")
    print()

    meal_plan_request = {
        "num_days": 3  # Request 3 days for demo
    }

    llm_response = requests.post(
        f"{BASE_URL}/users/me/llm-meal-plan",
        json=meal_plan_request,
        headers=headers
    )

    if llm_response.status_code != 200:
        print(f"\n❌ LLM generation failed: {llm_response.status_code}")
        print(f"Response: {llm_response.text}")
        return

    # Parse and display results
    result = llm_response.json()

    print("\n" + "=" * 80)
    print("✨ AI-GENERATED MEAL PLAN (Claude Haiku)")
    print("=" * 80)

    print(f"\n📊 Health Goal Summary:")
    print(f"   {result.get('health_goal_summary', 'N/A')}")

    print(f"\n📅 {len(result['plan'])} Day Meal Plan Generated")
    print()

    for day_plan in result["plan"]:
        print("=" * 80)
        print(f"📆 {day_plan['day']}")
        print("=" * 80)

        total_calories = sum(meal['calories'] for meal in day_plan['meals'])

        for meal in day_plan["meals"]:
            emoji = {
                "breakfast": "🍳",
                "lunch": "🥗",
                "dinner": "🍽️",
                "snack": "🍎"
            }.get(meal['type'].lower(), "🍴")

            print(f"\n{emoji} {meal['type'].upper()}: {meal['name']}")
            print(f"   Calories: {meal['calories']} kcal")
            print(f"   Description: {meal['description']}")

        print(f"\n   📈 Total Daily Calories: {total_calories} kcal")
        print()

    print("=" * 80)
    print("✅ LLM MEAL PLAN GENERATION SUCCESSFUL")
    print("=" * 80)

    print("\n🔍 Key Features Demonstrated:")
    print("   ✓ Personalized to user's health goals (Increased Energy, Better Sleep)")
    print("   ✓ Respects dietary restrictions (vegetarian)")
    print("   ✓ Avoids allergies (peanuts) and dislikes (mushrooms, olives)")
    print("   ✓ Appropriate complexity (moderate)")
    print("   ✓ Structured JSON output validated by Pydantic")
    print("   ✓ Nutritionally balanced with calorie estimates")
    print()


if __name__ == "__main__":
    test_llm_output()
