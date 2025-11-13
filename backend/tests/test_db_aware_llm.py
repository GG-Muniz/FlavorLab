"""
Test script to demonstrate database-aware LLM meal planning.
This script will:
1. Create a test user with health goals
2. Check what ingredients are associated with those health goals
3. Generate an LLM meal plan and show the prompt being sent
"""
import asyncio
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User
from app.models.entity import IngredientEntity
from app.services.llm_service import generate_meal_plan_prompt
from sqlalchemy import text


def setup_test_user(db: Session):
    """Create or get a test user with health goals."""
    # Check if test user exists
    test_user = db.query(User).filter(User.email == "test@example.com").first()

    if not test_user:
        # Try to use any existing user instead
        test_user = db.query(User).first()
        if test_user:
            print(f"✓ Using existing user: {test_user.email}")
        else:
            from app.services.auth import AuthService
            import uuid
            unique_username = f"testuser_{str(uuid.uuid4())[:8]}"
            test_user = AuthService.create_user(
                db=db,
                email="test@example.com",
                password="testpass123",
                username=unique_username,
                first_name="Test",
                last_name="User"
            )
            print("✓ Created new test user")
    else:
        print("✓ Using existing test user")

    # Set up health goals and survey data
    # Pillar IDs: 1=Heart Health, 2=Brain Health, 3=Bone Health, etc.
    test_user.preferences = {
        "health_goals": [1, 2],  # Heart Health and Brain Health
        "survey_data": {
            "healthPillars": ["Heart Health", "Brain Health"],
            "dietaryRestrictions": ["vegetarian"],
            "mealComplexity": "moderate",
            "dislikedIngredients": ["mushrooms"],
            "mealsPerDay": "3-meals-2-snacks",
            "allergies": [],
            "primaryGoal": "Improve cardiovascular and cognitive health"
        }
    }

    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(test_user, "preferences")
    db.commit()
    db.refresh(test_user)

    print(f"✓ Set health goals to: {test_user.preferences['health_goals']}")
    return test_user


def check_database_ingredients(db: Session, pillar_ids: list):
    """Check what ingredients exist for the given health pillars."""
    print("\n" + "="*80)
    print("CHECKING DATABASE FOR INGREDIENTS BY HEALTH PILLAR")
    print("="*80)

    all_ingredients = []
    for pillar_id in pillar_ids:
        ingredients = IngredientEntity.get_ingredients_by_pillar(
            db, pillar_id=pillar_id, limit=10
        )

        pillar_name = {1: "Heart Health", 2: "Brain Health", 3: "Bone Health"}.get(pillar_id, f"Pillar {pillar_id}")
        print(f"\n{pillar_name} (Pillar {pillar_id}):")

        if ingredients:
            for ing in ingredients:
                print(f"  - {ing.name}")
                all_ingredients.append(ing)
        else:
            print("  (No ingredients found)")

    # Deduplicate
    seen = set()
    unique_ingredients = [
        ing for ing in all_ingredients
        if not (ing.id in seen or seen.add(ing.id))
    ]

    print(f"\nTotal unique ingredients found: {len(unique_ingredients)}")
    return [ing.name for ing in unique_ingredients]


def show_generated_prompt(user: User, ingredient_names: list):
    """Display the prompt that will be sent to the LLM."""
    print("\n" + "="*80)
    print("GENERATED PROMPT FOR LLM")
    print("="*80)

    survey_data = user.preferences["survey_data"]
    prompt = generate_meal_plan_prompt(
        survey_data=survey_data,
        num_days=1,
        include_recipes=False,
        preferred_ingredients=ingredient_names if ingredient_names else None
    )

    print(prompt)
    print("\n" + "="*80)


def check_database_stats(db: Session):
    """Check how many ingredients are in the database."""
    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80)

    total_ingredients = db.query(IngredientEntity).count()
    print(f"Total ingredients in database: {total_ingredients}")

    # Check if there are any health pillar associations
    # The get_ingredients_by_pillar uses relationships table
    result = db.execute(text("SELECT COUNT(*) FROM relationships WHERE relationship_type = 'supports_pillar'"))
    relationship_count = result.scalar()
    print(f"Health pillar relationships: {relationship_count}")

    if total_ingredients == 0:
        print("\n⚠️  WARNING: No ingredients in database!")
        print("   The database may need to be populated with seed data.")

    if relationship_count == 0:
        print("\n⚠️  WARNING: No health pillar relationships found!")
        print("   Ingredients need to be linked to health pillars.")


def main():
    """Main test function."""
    print("="*80)
    print("DATABASE-AWARE LLM MEAL PLANNING TEST")
    print("="*80)

    db = SessionLocal()
    try:
        # Check database stats first
        check_database_stats(db)

        # Setup test user
        print("\n" + "="*80)
        print("SETTING UP TEST USER")
        print("="*80)
        user = setup_test_user(db)

        # Check what ingredients are in the database for user's health goals
        health_goals = user.preferences.get("health_goals", [])
        ingredient_names = check_database_ingredients(db, health_goals)

        # Show the prompt that will be generated
        show_generated_prompt(user, ingredient_names)

        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"User health goals: {user.preferences['survey_data']['healthPillars']}")
        print(f"Ingredients found in database: {len(ingredient_names)}")

        if ingredient_names:
            print("\n✓ SUCCESS: The LLM prompt now includes preferred ingredients from the database!")
            print("  The LLM will prioritize these ingredients when generating meal plans.")
        else:
            print("\n⚠️  NOTE: No ingredients found for the user's health goals.")
            print("  The LLM will generate meals without database-specific ingredient preferences.")
            print("  Consider populating the database with ingredient data.")

        print("\nTo test the actual LLM generation, you would need:")
        print("  1. A valid Anthropic API key in your .env file")
        print("  2. To call the /api/v1/users/me/llm-meal-plan endpoint")

    finally:
        db.close()


if __name__ == "__main__":
    main()
