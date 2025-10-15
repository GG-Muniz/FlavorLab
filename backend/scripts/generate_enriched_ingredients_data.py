#!/usr/bin/env python3
"""
Health Pillar Ingredient Enrichment Script

This script processes the entities.json file and enriches all ingredients with
health_outcomes data in the new pillar-mapped format. It handles:
1. Migration from old {"value": [...]} format to new list format
2. Ensuring all outcomes have pillar mappings
3. Inferring health outcomes from ingredient names when no explicit data exists

The enriched data is saved to health_pillar_ingredients_enriched.json.

Usage:
    cd /home/holberton/FlavorLab/backend
    python scripts/generate_enriched_ingredients_data.py
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# Add the backend directory to the Python path to import our modules
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

# Import the health pillar mapping function
from app.models.health_pillars import get_pillar_ids_for_outcome

# File paths
ENTITIES_FILE = os.path.join(backend_dir, "entities.json")
OUTPUT_FILE = os.path.join(backend_dir, "health_pillar_ingredients_enriched.json")


def get_current_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def transform_old_format_outcomes(old_outcomes: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """
    Transform old {"value": ["outcome1", "outcome2"]} format to new format.

    Args:
        old_outcomes: Dictionary with "value" key containing list of outcome strings

    Returns:
        List of outcome dictionaries with pillar mappings
    """
    transformed = []
    outcome_strings = old_outcomes.get("value", [])

    for outcome_str in outcome_strings:
        if isinstance(outcome_str, str) and outcome_str.strip():
            pillar_ids = get_pillar_ids_for_outcome(outcome_str)
            outcome_obj = {
                "outcome": outcome_str.strip(),
                "confidence": 3,  # Default confidence for existing data
                "added_at": get_current_utc_timestamp(),
                "pillars": pillar_ids
            }
            transformed.append(outcome_obj)

    return transformed


def ensure_pillar_mappings(outcomes_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ensure all outcomes in the list have proper pillar mappings.

    Args:
        outcomes_list: List of outcome dictionaries

    Returns:
        List of outcome dictionaries with ensured pillar mappings
    """
    enriched = []

    for outcome_obj in outcomes_list:
        if not isinstance(outcome_obj, dict):
            continue

        # Get the outcome string
        outcome_str = outcome_obj.get("outcome", "")
        if not outcome_str:
            continue

        # Ensure required fields with defaults
        enriched_outcome = {
            "outcome": outcome_str,
            "confidence": outcome_obj.get("confidence", 3),
            "added_at": outcome_obj.get("added_at", get_current_utc_timestamp())
        }

        # Preserve updated_at if it exists
        if "updated_at" in outcome_obj:
            enriched_outcome["updated_at"] = outcome_obj["updated_at"]

        # Re-calculate or ensure pillar mappings
        pillar_ids = get_pillar_ids_for_outcome(outcome_str)
        enriched_outcome["pillars"] = pillar_ids

        enriched.append(enriched_outcome)

    return enriched


def infer_health_outcomes_from_name(ingredient_name: str) -> List[Dict[str, Any]]:
    """
    Infer health outcomes from ingredient name using pillar mapping.

    This function uses the ingredient name to search for matching health pillars.
    For example, "Turmeric" might map to anti-inflammatory pillars, or "Ginger"
    might map to digestion-related pillars.

    Args:
        ingredient_name: Name of the ingredient

    Returns:
        List with single inferred outcome object, or empty list if no match
    """
    if not ingredient_name or not isinstance(ingredient_name, str):
        return []

    # Try to infer pillar IDs directly from the ingredient name
    pillar_ids = get_pillar_ids_for_outcome(ingredient_name)

    if pillar_ids:
        # We found matching pillars, create an inferred outcome
        inferred_outcome = {
            "outcome": ingredient_name,
            "confidence": 2,  # Lower confidence for inferred data
            "added_at": get_current_utc_timestamp(),
            "pillars": pillar_ids
        }
        return [inferred_outcome]

    return []


def process_ingredient(ingredient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single ingredient, enriching its health_outcomes field.

    This function:
    1. Handles existing health_outcomes in old or new format
    2. Ensures all outcomes have pillar mappings
    3. Infers outcomes from ingredient name if none exist

    Args:
        ingredient_data: Dictionary containing ingredient data

    Returns:
        Modified ingredient dictionary with enriched health_outcomes
    """
    transformed_outcomes = []

    # Get existing health_outcomes (may be missing, empty, or in various formats)
    existing_outcomes = ingredient_data.get("health_outcomes", None)

    # Case 1: Old format - {"value": ["outcome1", "outcome2"]}
    if isinstance(existing_outcomes, dict) and "value" in existing_outcomes:
        print(f"  Migrating old format for: {ingredient_data.get('name', 'Unknown')}")
        transformed_outcomes = transform_old_format_outcomes(existing_outcomes)

    # Case 2: New format - [{"outcome": "...", "pillars": [...]}]
    elif isinstance(existing_outcomes, list) and len(existing_outcomes) > 0:
        print(f"  Ensuring pillars for: {ingredient_data.get('name', 'Unknown')}")
        transformed_outcomes = ensure_pillar_mappings(existing_outcomes)

    # Case 3: No health_outcomes or empty - try to infer from name
    if not transformed_outcomes:
        ingredient_name = ingredient_data.get("name", "")
        if ingredient_name:
            inferred = infer_health_outcomes_from_name(ingredient_name)
            if inferred:
                print(f"  Inferred outcome from name: {ingredient_name}")
                transformed_outcomes = inferred
            else:
                print(f"  No health data for: {ingredient_name}")

    # Update the ingredient data with enriched health_outcomes
    ingredient_data["health_outcomes"] = transformed_outcomes

    return ingredient_data


def main():
    """Main execution function."""
    print("=" * 70)
    print("Health Pillar Ingredient Enrichment Script")
    print("=" * 70)
    print()

    # Check if input file exists
    if not os.path.exists(ENTITIES_FILE):
        print(f"ERROR: Input file not found: {ENTITIES_FILE}")
        sys.exit(1)

    print(f"Input file:  {ENTITIES_FILE}")
    print(f"Output file: {OUTPUT_FILE}")
    print()

    # Load entities.json
    print("Loading entities.json...")
    try:
        with open(ENTITIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to read file: {e}")
        sys.exit(1)

    # Extract entities list
    entities = data.get("entities", [])
    metadata = data.get("metadata", {})

    print(f"Loaded {len(entities)} entities")
    print(f"Metadata: {metadata}")
    print()

    # Statistics counters
    stats = {
        "total_processed": 0,
        "migrated_old_format": 0,
        "ensured_pillars": 0,
        "inferred_from_name": 0,
        "no_health_data": 0
    }

    # Process all ingredients
    print("Processing ingredients...")
    print("-" * 70)
    enriched_ingredients = []

    for idx, ingredient_data in enumerate(entities, 1):
        print(f"\n[{idx}/{len(entities)}] Processing: {ingredient_data.get('name', 'Unknown')}")

        # Track what operation was performed
        original_outcomes = ingredient_data.get("health_outcomes", None)

        # Process the ingredient
        enriched_ingredient = process_ingredient(ingredient_data)
        enriched_ingredients.append(enriched_ingredient)

        # Update statistics
        stats["total_processed"] += 1

        new_outcomes = enriched_ingredient.get("health_outcomes", [])

        if isinstance(original_outcomes, dict) and "value" in original_outcomes:
            stats["migrated_old_format"] += 1
        elif isinstance(original_outcomes, list) and len(original_outcomes) > 0:
            stats["ensured_pillars"] += 1
        elif new_outcomes:
            stats["inferred_from_name"] += 1
        else:
            stats["no_health_data"] += 1

    print()
    print("-" * 70)
    print()

    # Prepare output data structure
    output_data = {
        "metadata": {
            "total_entities": len(enriched_ingredients),
            "original_file": "entities.json",
            "enrichment_timestamp": get_current_utc_timestamp(),
            "version": "1.1.0",
            "enrichment_stats": stats,
            "original_metadata": metadata
        },
        "entities": enriched_ingredients
    }

    # Save enriched data
    print(f"Saving enriched data to: {OUTPUT_FILE}")
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print("✓ Successfully saved enriched data")
    except Exception as e:
        print(f"ERROR: Failed to save output file: {e}")
        sys.exit(1)

    # Print summary statistics
    print()
    print("=" * 70)
    print("ENRICHMENT SUMMARY")
    print("=" * 70)
    print(f"Total ingredients processed:     {stats['total_processed']}")
    print(f"  - Migrated from old format:    {stats['migrated_old_format']}")
    print(f"  - Ensured pillar mappings:     {stats['ensured_pillars']}")
    print(f"  - Inferred from name:          {stats['inferred_from_name']}")
    print(f"  - No health data found:        {stats['no_health_data']}")
    print()

    # Calculate enrichment percentage
    enriched_count = stats['total_processed'] - stats['no_health_data']
    enrichment_percentage = (enriched_count / stats['total_processed'] * 100) if stats['total_processed'] > 0 else 0
    print(f"Enrichment rate: {enrichment_percentage:.1f}% ({enriched_count}/{stats['total_processed']} ingredients)")
    print()

    # Sample enriched ingredients
    print("Sample enriched ingredients:")
    print("-" * 70)
    sample_count = min(5, len(enriched_ingredients))
    for ingredient in enriched_ingredients[:sample_count]:
        name = ingredient.get("name", "Unknown")
        outcomes = ingredient.get("health_outcomes", [])
        print(f"\n  {name}:")
        if outcomes:
            for outcome in outcomes[:2]:  # Show first 2 outcomes
                pillars = outcome.get("pillars", [])
                confidence = outcome.get("confidence", 0)
                print(f"    - {outcome.get('outcome', 'N/A')} (confidence: {confidence}, pillars: {pillars})")
        else:
            print("    (no health outcomes)")

    print()
    print("=" * 70)
    print("Enrichment complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
