#!/usr/bin/env python3
"""
LLM Meal Plan Generator Behavior Test Script

This script tests the Claude Haiku-powered meal plan generator against
multiple user personas to validate adherence to dietary restrictions,
allergies, preferences, and health goals.

Usage:
    cd /home/holberton/FlavorLab/backend
    python scripts/test_llm_behavior.py
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# Add backend directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

# Import application components
from app.database import SessionLocal
from app.models.user import User
from app.models.health_pillars import HEALTH_PILLARS
from app.services import llm_service


# ============================================================================
# USER PERSONAS (TEST CASES)
# ============================================================================

PERSONAS = [
    {
        "name": "The Celiac Vegan",
        "description": "Gluten-free vegan with multiple allergies",
        "survey_data": {
            "healthPillars": ["Improved Digestion", "Increased Energy"],
            "dietaryRestrictions": ["vegetarian", "gluten-free"],
            "allergies": ["dairy", "peanuts"],
            "dislikedIngredients": ["mushrooms", "eggplant"],
            "mealsPerDay": "3-meals-2-snacks",
            "mealComplexity": "moderate",
            "primaryGoal": "weight-loss"
        },
        "violations_to_check": {
            "allergens": ["dairy", "milk", "cheese", "yogurt", "butter", "cream",
                         "peanut", "peanuts", "peanut butter"],
            "gluten": ["bread", "pasta", "wheat", "flour", "barley", "rye",
                      "couscous", "seitan", "breadcrumb"],
            "meat": ["chicken", "beef", "pork", "turkey", "lamb", "fish",
                    "salmon", "tuna", "meat"],
            "disliked": ["mushroom", "eggplant"]
        }
    },
    {
        "name": "The Keto Bodybuilder",
        "description": "High-protein keto with shellfish allergy",
        "survey_data": {
            "healthPillars": ["Muscle Recovery", "Mental Clarity"],
            "dietaryRestrictions": ["keto"],
            "allergies": ["shellfish"],
            "dislikedIngredients": ["avocado"],
            "mealsPerDay": "6",
            "mealComplexity": "moderate",
            "primaryGoal": "muscle-gain"
        },
        "violations_to_check": {
            "allergens": ["shrimp", "crab", "lobster", "shellfish", "prawns"],
            "high_carb": ["rice", "pasta", "bread", "potato", "sweet potato",
                         "quinoa", "oats", "banana", "apple"],
            "disliked": ["avocado"]
        }
    },
    {
        "name": "The Adventurous Sleeper",
        "description": "Sleep-focused with complex meals, minimal restrictions",
        "survey_data": {
            "healthPillars": ["Better Sleep", "Inflammation Reduction"],
            "dietaryRestrictions": [],
            "allergies": [],
            "dislikedIngredients": ["cilantro"],
            "mealsPerDay": "3",
            "mealComplexity": "complex",
            "primaryGoal": "wellness"
        },
        "violations_to_check": {
            "disliked": ["cilantro"]
        }
    },
    {
        "name": "The Empty Profile (Edge Case)",
        "description": "Minimal preferences to test default behavior",
        "survey_data": {
            "healthPillars": ["Heart Health"],
            "dietaryRestrictions": [],
            "allergies": [],
            "dislikedIngredients": [],
            "mealsPerDay": "3-meals-2-snacks",
            "mealComplexity": "simple",
            "primaryGoal": "general health"
        },
        "violations_to_check": {}
    }
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def translate_pillars_to_ids(pillar_names: List[str]) -> List[int]:
    """Convert pillar names to IDs."""
    pillar_name_to_id = {
        data["name"]: pillar_id
        for pillar_id, data in HEALTH_PILLARS.items()
    }
    return [pillar_name_to_id[name] for name in pillar_names if name in pillar_name_to_id]


def create_mock_user(persona: Dict[str, Any]) -> User:
    """Create a mock User object with persona's preferences."""
    user = User()
    user.id = 999
    user.email = f"{persona['name'].lower().replace(' ', '_')}@test.com"
    user.username = persona['name'].replace(' ', '_')

    # Set up preferences
    survey_data = persona['survey_data']
    health_goal_ids = translate_pillars_to_ids(survey_data['healthPillars'])

    user.preferences = {
        "health_goals": health_goal_ids,
        "survey_data": survey_data
    }

    return user


def check_violations(meal, violations_config: Dict[str, List[str]]) -> List[str]:
    """
    Check a meal for violations against user constraints.
    Returns list of violation messages.
    """
    violations = []

    # Combine all searchable text from the meal
    searchable_text = " ".join([
        meal.name.lower(),
        meal.description.lower(),
        " ".join(meal.ingredients or []).lower() if meal.ingredients else ""
    ])

    # Safe compound ingredients that should NOT trigger violations
    safe_compounds = {
        "butter": ["almond butter", "peanut butter", "cashew butter", "sunflower butter"],
        "cream": ["coconut cream", "cashew cream", "oat cream"],
        "milk": ["coconut milk", "almond milk", "oat milk", "soy milk", "cashew milk"],
        "bread": ["gluten-free bread"],
        "cheese": ["cashew cheese", "nutritional yeast"],
        "yogurt": ["coconut yogurt", "almond yogurt"]
    }

    # Check each violation category
    for category, banned_items in violations_config.items():
        for item in banned_items:
            item_lower = item.lower()

            # Check if the banned item appears in text
            if item_lower in searchable_text:
                # Check if it's actually a safe compound ingredient
                is_safe = False
                if item_lower in safe_compounds:
                    for safe_variant in safe_compounds[item_lower]:
                        if safe_variant in searchable_text:
                            is_safe = True
                            break

                # Only report as violation if not a safe compound
                if not is_safe:
                    violations.append(
                        f"❌ {category.upper()} VIOLATION: '{item}' found in {meal.type} - {meal.name}"
                    )

    return violations


def analyze_meal_structure(plan, expected_structure: str) -> str:
    """Analyze if meal structure matches expectations."""
    day = plan[0]
    meal_types = [meal.type for meal in day.meals]

    structure_map = {
        "3": 3,
        "3-meals-2-snacks": 5,
        "6": 6
    }

    expected_count = structure_map.get(expected_structure, 5)
    actual_count = len(meal_types)

    if actual_count == expected_count:
        return f"✅ Meal structure correct: {actual_count} meals"
    else:
        return f"⚠️  Meal structure mismatch: Expected {expected_count}, got {actual_count} meals"


def print_separator(char="=", length=80):
    """Print a separator line."""
    print(char * length)


def print_header(text: str):
    """Print a formatted header."""
    print_separator()
    print(f"  {text}")
    print_separator()


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def test_persona(persona: Dict[str, Any], db):
    """Test a single persona and report results."""
    print_header(f"TESTING PERSONA: {persona['name']}")
    print(f"Description: {persona['description']}\n")

    # Create mock user
    mock_user = create_mock_user(persona)
    print(f"Health Goals: {persona['survey_data']['healthPillars']}")
    print(f"Dietary Restrictions: {persona['survey_data']['dietaryRestrictions']}")
    print(f"Allergies: {persona['survey_data']['allergies']}")
    print(f"Disliked: {persona['survey_data']['dislikedIngredients']}")
    print(f"Meals/Day: {persona['survey_data']['mealsPerDay']}")
    print()

    try:
        # Generate meal plan
        print("🔄 Generating meal plan with Claude Haiku...")
        daily_plans = await llm_service.generate_llm_meal_plan(
            user=mock_user,
            num_days=1,
            include_recipes=True,
            db=db
        )

        print("✅ Meal plan generated successfully!\n")

        # Analyze structure
        structure_result = analyze_meal_structure(
            daily_plans,
            persona['survey_data']['mealsPerDay']
        )
        print(structure_result)
        print()

        # Check for violations
        print("🔍 VIOLATION ANALYSIS:")
        print_separator("-")

        all_violations = []
        for day in daily_plans:
            for meal in day.meals:
                violations = check_violations(meal, persona['violations_to_check'])
                all_violations.extend(violations)

        if all_violations:
            print("⚠️  VIOLATIONS DETECTED:")
            for violation in all_violations:
                print(f"  {violation}")
        else:
            print("✅ No violations detected - all constraints respected!")

        print()

        # Print full meal plan for manual review
        print("📋 GENERATED MEAL PLAN (Manual Review):")
        print_separator("-")

        for day in daily_plans:
            print(f"\n{day.day}:")
            for meal in day.meals:
                print(f"\n  [{meal.type.upper()}] {meal.name} ({meal.calories} cal)")
                print(f"  Description: {meal.description}")

                if meal.ingredients:
                    print(f"  Ingredients: {', '.join(meal.ingredients[:5])}", end="")
                    if len(meal.ingredients) > 5:
                        print(f" ... ({len(meal.ingredients)} total)")
                    else:
                        print()

                if meal.nutrition:
                    print(f"  Nutrition: Protein {meal.nutrition.get('protein', 'N/A')}, "
                          f"Carbs {meal.nutrition.get('carbs', 'N/A')}, "
                          f"Fat {meal.nutrition.get('fat', 'N/A')}")

        # Print full JSON for detailed inspection
        print("\n")
        print_separator("-")
        print("📄 FULL JSON OUTPUT:")
        print_separator("-")

        plan_dict = [
            {
                "day": day.day,
                "meals": [
                    {
                        "type": meal.type,
                        "name": meal.name,
                        "calories": meal.calories,
                        "description": meal.description,
                        "ingredients": meal.ingredients,
                        "servings": meal.servings,
                        "prep_time_minutes": meal.prep_time_minutes,
                        "cook_time_minutes": meal.cook_time_minutes,
                        "instructions": meal.instructions,
                        "nutrition": meal.nutrition
                    }
                    for meal in day.meals
                ]
            }
            for day in daily_plans
        ]

        print(json.dumps(plan_dict, indent=2))

        # Summary
        print("\n")
        print_separator("-")
        if not all_violations:
            print("✅ PERSONA TEST PASSED")
        else:
            print(f"⚠️  PERSONA TEST COMPLETED WITH {len(all_violations)} VIOLATION(S)")
        print_separator("-")

    except llm_service.LLMResponseError as e:
        print(f"❌ LLM ERROR: {e}")
        print("The LLM failed to generate a valid meal plan for this persona.")
    except ValueError as e:
        print(f"❌ VALIDATION ERROR: {e}")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    print("\n\n")


async def main():
    """Main test orchestrator."""
    print_header("LLM MEAL PLAN GENERATOR BEHAVIOR TEST SUITE")
    print(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Personas: {len(PERSONAS)}\n")

    # Create database session
    db = SessionLocal()

    try:
        # Test each persona
        for idx, persona in enumerate(PERSONAS, 1):
            print(f"\n{'='*80}")
            print(f"PERSONA {idx}/{len(PERSONAS)}")
            print(f"{'='*80}\n")

            await test_persona(persona, db)

            # Brief pause between tests to avoid rate limiting
            if idx < len(PERSONAS):
                print("⏳ Pausing 2 seconds before next test...")
                await asyncio.sleep(2)

        # Final summary
        print_header("TEST SUITE COMPLETE")
        print(f"✅ Tested {len(PERSONAS)} personas")
        print(f"📊 Review the output above for violations and quality assessment")
        print()
        print("NOTE: Some violations may be false positives (e.g., 'butter' in 'peanut butter')")
        print("      Always perform manual review of the JSON output.")
        print_separator()

    finally:
        db.close()
        print("\n🔒 Database session closed.")


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("Starting LLM Behavior Test Script...")
    print("="*80 + "\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "="*80)
    print("Test script completed.")
    print("="*80 + "\n")
