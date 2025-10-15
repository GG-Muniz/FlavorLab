"""
Test with varied dietary preferences to show LLM flexibility.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_vegan_athlete():
    """Test LLM with vegan athlete profile."""

    print("=" * 80)
    print("SCENARIO: Vegan Athlete - High Protein, Muscle Recovery")
    print("=" * 80)

    # Login
    login_data = {
        "email": "testnutrition@example.com",
        "password": "TestPassword123"
    }

    login_response = requests.post(f"{BASE_URL}/users/login", json=login_data)
    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Submit vegan athlete survey
    print("\n📋 User Profile:")
    survey_data = {
        "healthPillars": ["Muscle Recovery", "Increased Energy", "Heart Health"],
        "dietaryRestrictions": ["vegan"],
        "mealComplexity": "complex",
        "dislikedIngredients": ["tofu"],
        "mealsPerDay": "5",
        "allergies": ["soy"],
        "primaryGoal": "build muscle on a plant-based diet"
    }

    print(f"   🎯 Goals: {', '.join(survey_data['healthPillars'])}")
    print(f"   🌱 Diet: {', '.join(survey_data['dietaryRestrictions'])}")
    print(f"   ⚠️  Allergies: {', '.join(survey_data['allergies'])}")
    print(f"   🚫 Dislikes: {', '.join(survey_data['dislikedIngredients'])}")
    print(f"   🍽️  Meals/day: {survey_data['mealsPerDay']}")

    requests.post(f"{BASE_URL}/users/me/survey", json=survey_data, headers=headers)

    # Generate meal plan
    print("\n⏳ Generating AI meal plan...")

    llm_response = requests.post(
        f"{BASE_URL}/users/me/llm-meal-plan",
        json={"num_days": 2},
        headers=headers
    )

    if llm_response.status_code != 200:
        print(f"❌ Failed: {llm_response.status_code}")
        print(llm_response.text)
        return

    result = llm_response.json()

    print("\n" + "=" * 80)
    print("✨ CLAUDE HAIKU OUTPUT")
    print("=" * 80)

    for day_plan in result["plan"]:
        print(f"\n📆 {day_plan['day']}:")
        print("-" * 80)

        for meal in day_plan["meals"]:
            print(f"\n  {meal['type'].upper()}: {meal['name']}")
            print(f"  └─ {meal['calories']} kcal")
            print(f"  └─ {meal['description']}")

        total_cals = sum(m['calories'] for m in day_plan['meals'])
        print(f"\n  💪 Daily Total: {total_cals} kcal")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_vegan_athlete()
