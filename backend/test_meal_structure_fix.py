"""
Test the FIXED meal structure enforcement.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"


def test_meal_structure_fixed():
    """Test meal structure with strengthened prompt."""
    print("=" * 80)
    print("TESTING FIXED MEAL STRUCTURE ENFORCEMENT")
    print("Requirement: 3 MEALS + 2 SNACKS = 5 items per day")
    print("=" * 80)

    # Login
    login_data = {
        "email": "testnutrition@example.com",
        "password": "TestPassword123"
    }
    response = requests.post(f"{BASE_URL}/users/login", json=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Submit survey with 3-meals-2-snacks
    survey_data = {
        "healthPillars": ["Increased Energy"],
        "dietaryRestrictions": [],
        "mealComplexity": "simple",
        "dislikedIngredients": [],
        "mealsPerDay": "3-meals-2-snacks",  # CRITICAL TEST
        "allergies": [],
        "primaryGoal": "maintain energy"
    }

    requests.post(f"{BASE_URL}/users/me/survey", json=survey_data, headers=headers)

    print("\n⏳ Generating meal plan with STRENGTHENED PROMPT...")
    print("   The prompt now has:")
    print("   - 🚨 MANDATORY section with explicit structure")
    print("   - Example JSON showing 5 items")
    print("   - Pre-response checklist")
    print()

    response = requests.post(
        f"{BASE_URL}/users/me/llm-meal-plan",
        json={"num_days": 2},
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()

        print("📊 RESULTS:")
        print("=" * 80)

        total_pass = 0
        total_fail = 0

        for day in result['plan']:
            meal_count = len(day['meals'])
            snack_count = sum(1 for m in day['meals'] if m['type'].lower() == 'snack')

            print(f"\n📆 {day['day']}:")
            print(f"   Total items: {meal_count}/5 ", end="")

            if meal_count == 5:
                print("✅ CORRECT")
                total_pass += 1
            else:
                print("❌ WRONG")
                total_fail += 1

            print(f"   Snacks: {snack_count}/2 ", end="")
            if snack_count == 2:
                print("✅")
            else:
                print("❌")

            print(f"\n   Meal breakdown:")
            for i, meal in enumerate(day['meals'], 1):
                emoji = "🍽️" if meal['type'] != 'snack' else "🍎"
                print(f"   {i}. {emoji} {meal['type']:12} - {meal['name']}")

        print("\n" + "=" * 80)
        print(f"📊 SUMMARY: {total_pass} days passed, {total_fail} days failed")

        if total_fail == 0:
            print("🎉 SUCCESS! Meal structure is now enforced correctly!")
        else:
            print("⚠️  Still needs work. The LLM is not following the structure.")
            print("\nPossible solutions:")
            print("1. Increase max_tokens (currently 4096)")
            print("2. Add explicit count validation in post-processing")
            print("3. Use a more explicit JSON schema constraint")
            print("4. Try different temperature settings")

    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    test_meal_structure_fixed()
