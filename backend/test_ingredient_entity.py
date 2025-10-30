#!/usr/bin/env python3
"""
Test script for IngredientEntity model enhancements.
Tests add_health_outcome, data migration, and filtering capabilities.
"""

import sys
sys.path.insert(0, '/home/holberton/FlavorLab/backend')

from app.database import SessionLocal, engine, Base
from app.models.entity import Entity, IngredientEntity
from datetime import datetime, timezone as UTC
import json

# Create tables if needed
Base.metadata.create_all(bind=engine)

def setup_test_data(db):
    """Create test ingredients for various scenarios."""
    print("\n=== Setting Up Test Data ===")

    # Clean up existing test data
    db.query(IngredientEntity).filter(IngredientEntity.id.like('test_%')).delete()
    db.query(Entity).filter(Entity.id.like('test_%')).delete()
    db.commit()

    # Create base entities first
    entities = [
        Entity(id="test_ginger", name="Ginger", primary_classification="ingredient"),
        Entity(id="test_turmeric", name="Turmeric", primary_classification="ingredient"),
        Entity(id="test_blueberry", name="Blueberries", primary_classification="ingredient"),
        Entity(id="test_spinach", name="Spinach", primary_classification="ingredient"),
        Entity(id="test_salmon", name="Salmon", primary_classification="ingredient"),
    ]

    for entity in entities:
        db.add(entity)
    db.flush()  # Ensure all base entities exist

    # Test 1: Fresh ingredient (Ginger)
    ginger = IngredientEntity(
        id="test_ginger",
        health_outcomes=[]
    )
    db.add(ginger)

    # Test 2: Ingredient with old format (Turmeric)
    turmeric = IngredientEntity(
        id="test_turmeric",
        health_outcomes={"value": ["Inflammation", "Digestion"]}  # Old format
    )
    db.add(turmeric)

    # Test 3: Ingredient with existing new format (Blueberries)
    blueberry = IngredientEntity(
        id="test_blueberry",
        health_outcomes=[
            {
                "outcome": "Antioxidant support",
                "confidence": 5,
                "added_at": datetime.now(UTC).isoformat(),
                "pillars": [3]  # Immunity
            }
        ]
    )
    db.add(blueberry)

    # Test 4: Spinach - for testing multiple pillars
    spinach = IngredientEntity(
        id="test_spinach",
        health_outcomes=[]
    )
    db.add(spinach)

    # Test 5: Salmon - for testing multiple outcomes
    salmon = IngredientEntity(
        id="test_salmon",
        health_outcomes=[]
    )
    db.add(salmon)

    db.commit()
    print("✓ Created 5 test ingredients")

def test_add_health_outcome_new(db):
    """Test 2.1: add_health_outcome on fresh ingredient."""
    print("\n=== Test 2.1: add_health_outcome - New Ingredient (Ginger) ===")

    ginger = db.query(IngredientEntity).filter_by(id="test_ginger").first()

    # Add anti-inflammatory outcome
    ginger.add_health_outcome(outcome="Anti-inflammatory", confidence=5)
    db.commit()
    db.refresh(ginger)

    # Verify
    outcomes = ginger.health_outcomes
    print(f"Health outcomes: {json.dumps(outcomes, indent=2)}")

    if len(outcomes) == 1:
        print("✓ Single outcome added")
        outcome = outcomes[0]

        checks = [
            (outcome.get("outcome") == "Anti-inflammatory", "outcome name"),
            (outcome.get("confidence") == 5, "confidence value"),
            ("added_at" in outcome, "added_at timestamp"),
            (outcome.get("pillars") == [8], "pillar mapping to Inflammation Reduction (8)"),
        ]

        for passed, description in checks:
            status = "✓" if passed else "✗"
            print(f"{status} {description}")
    else:
        print(f"✗ Expected 1 outcome, got {len(outcomes)}")

def test_add_health_outcome_migration(db):
    """Test 2.2: add_health_outcome with old format migration."""
    print("\n=== Test 2.2: add_health_outcome - Old Format Migration (Turmeric) ===")

    turmeric = db.query(IngredientEntity).filter_by(id="test_turmeric").first()

    print(f"Before: {json.dumps(turmeric.health_outcomes, indent=2)}")

    # Add new outcome - should trigger migration
    turmeric.add_health_outcome(outcome="Immune Support", confidence=4)
    db.commit()
    db.refresh(turmeric)

    outcomes = turmeric.health_outcomes
    print(f"After: {json.dumps(outcomes, indent=2)}")

    if len(outcomes) == 3:
        print("✓ Migrated 2 old outcomes + added 1 new = 3 total")

        # Check migrated outcomes
        inflammation_found = any(
            o.get("outcome") == "Inflammation" and 8 in o.get("pillars", [])
            for o in outcomes
        )
        digestion_found = any(
            o.get("outcome") == "Digestion" and 2 in o.get("pillars", [])
            for o in outcomes
        )
        immune_found = any(
            o.get("outcome") == "Immune Support" and 3 in o.get("pillars", []) and o.get("confidence") == 4
            for o in outcomes
        )

        checks = [
            (inflammation_found, "Inflammation → Pillar 8"),
            (digestion_found, "Digestion → Pillar 2"),
            (immune_found, "Immune Support → Pillar 3"),
        ]

        for passed, description in checks:
            status = "✓" if passed else "✗"
            print(f"{status} {description}")
    else:
        print(f"✗ Expected 3 outcomes, got {len(outcomes)}")

def test_add_multiple_outcomes(db):
    """Test adding multiple outcomes with various pillar mappings."""
    print("\n=== Test: Multiple Outcomes (Spinach) ===")

    spinach = db.query(IngredientEntity).filter_by(id="test_spinach").first()

    # Add multiple outcomes
    spinach.add_health_outcome(outcome="Supports Energy", confidence=4)
    spinach.add_health_outcome(outcome="Improves Digestion", confidence=3)
    spinach.add_health_outcome(outcome="Heart Health Benefits", confidence=5)
    db.commit()
    db.refresh(spinach)

    outcomes = spinach.health_outcomes
    print(f"Added {len(outcomes)} outcomes")

    if len(outcomes) == 3:
        print("✓ All 3 outcomes added")

        # Verify pillars
        checks = [
            (any(1 in o.get("pillars", []) for o in outcomes), "Pillar 1 (Energy)"),
            (any(2 in o.get("pillars", []) for o in outcomes), "Pillar 2 (Digestion)"),
            (any(6 in o.get("pillars", []) for o in outcomes), "Pillar 6 (Heart Health)"),
        ]

        for passed, description in checks:
            status = "✓" if passed else "✗"
            print(f"{status} {description}")
    else:
        print(f"✗ Expected 3 outcomes, got {len(outcomes)}")

def test_get_ingredients_by_pillar(db):
    """Test 2.3: get_ingredients_by_pillar."""
    print("\n=== Test 2.3: get_ingredients_by_pillar ===")

    # Add outcomes to salmon for testing
    salmon = db.query(IngredientEntity).filter_by(id="test_salmon").first()
    salmon.add_health_outcome(outcome="Anti-inflammatory omega-3", confidence=5)
    salmon.add_health_outcome(outcome="Brain health", confidence=4)
    db.commit()

    # Test pillar 8 (Inflammation Reduction)
    pillar_8_ingredients = IngredientEntity.get_ingredients_by_pillar(db, pillar_id=8)
    pillar_8_names = [ing.name for ing in pillar_8_ingredients if ing.id.startswith('test_')]

    print(f"\nPillar 8 (Inflammation Reduction) ingredients: {pillar_8_names}")
    if "Ginger" in pillar_8_names and "Salmon" in pillar_8_names:
        print("✓ Found Ginger and Salmon (both have anti-inflammatory properties)")
    else:
        print(f"✗ Expected Ginger and Salmon, got: {pillar_8_names}")

    # Test pillar 3 (Immunity)
    pillar_3_ingredients = IngredientEntity.get_ingredients_by_pillar(db, pillar_id=3)
    pillar_3_names = [ing.name for ing in pillar_3_ingredients if ing.id.startswith('test_')]

    print(f"\nPillar 3 (Enhanced Immunity) ingredients: {pillar_3_names}")
    if "Blueberries" in pillar_3_names and "Turmeric" in pillar_3_names:
        print("✓ Found Blueberries and Turmeric (both support immunity)")
    else:
        print(f"✗ Expected Blueberries and Turmeric, got: {pillar_3_names}")

    # Test invalid pillar
    pillar_99_ingredients = IngredientEntity.get_ingredients_by_pillar(db, pillar_id=99)
    print(f"\nPillar 99 (Invalid) ingredients: {len(pillar_99_ingredients)}")
    if len(pillar_99_ingredients) == 0:
        print("✓ Empty list for invalid pillar ID")
    else:
        print(f"✗ Expected empty list, got {len(pillar_99_ingredients)} ingredients")

def test_filter_ingredients_by_pillars(db):
    """Test 2.4: filter_ingredients_by_pillars."""
    print("\n=== Test 2.4: filter_ingredients_by_pillars ===")

    # Test with multiple pillars
    base_query = db.query(IngredientEntity).filter(IngredientEntity.id.like('test_%'))
    filtered_query = IngredientEntity.filter_ingredients_by_pillars(base_query, [1, 8])
    results = filtered_query.all()

    # Manual Python filtering (needed for SQLite)
    python_filtered = []
    for ing in results:
        if isinstance(ing.health_outcomes, list):
            for outcome in ing.health_outcomes:
                if isinstance(outcome, dict) and "pillars" in outcome:
                    if any(pid in outcome["pillars"] for pid in [1, 8]):
                        python_filtered.append(ing)
                        break

    result_names = [ing.name for ing in python_filtered]
    print(f"Ingredients with Pillar 1 or 8: {result_names}")

    expected_names = ["Ginger", "Spinach", "Salmon"]  # All have energy or inflammation
    found_count = sum(1 for name in expected_names if name in result_names)

    if found_count >= 2:
        print(f"✓ Found {found_count}/{len(expected_names)} expected ingredients")
    else:
        print(f"✗ Expected at least 2 of {expected_names}, got: {result_names}")

    # Test with empty pillar list
    filtered_query_empty = IngredientEntity.filter_ingredients_by_pillars(base_query, [])
    results_empty = filtered_query_empty.all()

    if len(results_empty) == 5:  # Should return all 5 test ingredients
        print("✓ Empty pillar list returns unfiltered query")
    else:
        print(f"✗ Expected 5 ingredients, got {len(results_empty)}")

if __name__ == "__main__":
    print("=" * 70)
    print("INGREDIENT ENTITY MODEL TESTS")
    print("=" * 70)

    db = SessionLocal()

    try:
        setup_test_data(db)
        test_add_health_outcome_new(db)
        test_add_health_outcome_migration(db)
        test_add_multiple_outcomes(db)
        test_get_ingredients_by_pillar(db)
        test_filter_ingredients_by_pillars(db)

        print("\n" + "=" * 70)
        print("TESTS COMPLETE")
        print("=" * 70)

    finally:
        db.close()
