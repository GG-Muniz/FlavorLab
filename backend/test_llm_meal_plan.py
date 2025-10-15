"""
Test script for LLM-based meal plan generation endpoint.

This script tests the new /api/v1/users/me/llm-meal-plan endpoint.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_llm_meal_plan():
    """Test the LLM meal plan generation endpoint."""

    print("=" * 60)
    print("Testing LLM Meal Plan Generation Endpoint")
    print("=" * 60)

    # Step 1: Login
    print("\n[Step 1] Authenticating...")
    login_data = {
        "email": "testnutrition@example.com",
        "password": "TestPassword123"
    }

    login_response = requests.post(f"{BASE_URL}/users/login", json=login_data)

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return

    token = login_response.json()["access_token"]
    print("✓ Authentication successful")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 2: Submit survey data (if not already done)
    print("\n[Step 2] Ensuring survey data exists...")
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
        print("✓ Survey data submitted successfully")
    else:
        print(f"⚠ Survey submission status: {survey_response.status_code}")

    # Step 3: Generate LLM meal plan
    print("\n[Step 3] Generating LLM meal plan (this may take 10-30 seconds)...")
    meal_plan_request = {
        "num_days": 3  # Request 3 days for faster testing
    }

    llm_response = requests.post(
        f"{BASE_URL}/users/me/llm-meal-plan",
        json=meal_plan_request,
        headers=headers
    )

    print(f"Response status: {llm_response.status_code}")

    if llm_response.status_code != 200:
        print(f"❌ LLM meal plan generation failed")
        print(f"Status code: {llm_response.status_code}")
        print(f"Response: {llm_response.text}")
        return

    # Parse and display results
    result = llm_response.json()

    print("\n" + "=" * 60)
    print("✓ LLM MEAL PLAN GENERATED SUCCESSFULLY")
    print("=" * 60)

    print(f"\nHealth Goal Summary:")
    print(f"  {result.get('health_goal_summary', 'N/A')}")

    print(f"\nMeal Plan ({len(result['plan'])} days):")
    print("-" * 60)

    for day in result["plan"]:
        print(f"\n{day['day']}:")
        for meal in day["meals"]:
            print(f"  • {meal['type'].upper()}: {meal['name']}")
            print(f"    Calories: {meal['calories']}")
            print(f"    Description: {meal['description'][:80]}...")

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_llm_meal_plan()
