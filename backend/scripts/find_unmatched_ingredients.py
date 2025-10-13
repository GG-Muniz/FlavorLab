#!/usr/bin/env python3
"""
Diagnostic Script: Find Ingredients Without Health Pillar Mappings

This script compares the original entities.json with the enriched
health_pillar_ingredients_enriched.json file to identify which ingredients
were not successfully enriched with health pillar mappings.

Usage:
    cd /home/holberton/FlavorLab/backend
    python scripts/find_unmatched_ingredients.py
"""

import json
import os
import sys
from typing import List, Set, Dict, Any

# File paths
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
ORIGINAL_FILE = os.path.join(backend_dir, "entities.json")
ENRICHED_FILE = os.path.join(backend_dir, "health_pillar_ingredients_enriched.json")


def load_json_file(filepath: str) -> Dict[str, Any]:
    """
    Load and parse a JSON file.

    Args:
        filepath: Path to the JSON file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        SystemExit: If file cannot be read or parsed
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON in {filepath}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to read {filepath}: {e}")
        sys.exit(1)


def get_enriched_ids(enriched_data: Dict[str, Any]) -> Set[Any]:
    """
    Extract IDs of all ingredients that have health_outcomes data.

    Args:
        enriched_data: Parsed enriched JSON data

    Returns:
        Set of ingredient IDs that have been enriched with health outcomes
    """
    enriched_ids = set()
    enriched_ingredients = enriched_data.get("entities", [])

    for ingredient in enriched_ingredients:
        health_outcomes = ingredient.get("health_outcomes", [])

        # Check if health_outcomes exists and is not empty
        if health_outcomes and len(health_outcomes) > 0:
            # Use 'id' field as the unique identifier
            ingredient_id = ingredient.get("id")
            if ingredient_id is not None:
                enriched_ids.add(ingredient_id)

    return enriched_ids


def find_unmatched_ingredients(
    original_data: Dict[str, Any],
    enriched_ids: Set[Any]
) -> List[Dict[str, Any]]:
    """
    Find ingredients from the original dataset that were not enriched.

    Args:
        original_data: Original entities.json data
        enriched_ids: Set of IDs that were successfully enriched

    Returns:
        List of ingredient dictionaries that were not enriched
    """
    unmatched = []
    all_ingredients = original_data.get("entities", [])

    for ingredient in all_ingredients:
        ingredient_id = ingredient.get("id")

        # Check if this ingredient was NOT enriched
        if ingredient_id not in enriched_ids:
            unmatched.append({
                "id": ingredient_id,
                "name": ingredient.get("name", "Unknown"),
                "primary_classification": ingredient.get("primary_classification", "Unknown")
            })

    return unmatched


def print_results(
    unmatched: List[Dict[str, Any]],
    total_count: int,
    enriched_count: int
):
    """
    Print diagnostic results in a formatted way.

    Args:
        unmatched: List of unmatched ingredient dictionaries
        total_count: Total number of ingredients in original file
        enriched_count: Number of successfully enriched ingredients
    """
    print()
    print("=" * 70)
    print("INGREDIENTS WITHOUT HEALTH PILLAR MAPPINGS")
    print("=" * 70)
    print()

    if not unmatched:
        print("✓ All ingredients have been enriched with health pillar mappings!")
        print()
        return

    # Group by primary_classification for better organization
    by_classification = {}
    for ing in unmatched:
        classification = ing["primary_classification"]
        if classification not in by_classification:
            by_classification[classification] = []
        by_classification[classification].append(ing)

    # Print grouped results
    for classification in sorted(by_classification.keys()):
        ingredients = by_classification[classification]
        print(f"\n{classification.upper()} ({len(ingredients)} items)")
        print("-" * 70)
        for ing in sorted(ingredients, key=lambda x: x["name"]):
            print(f"  • {ing['name']} (ID: {ing['id']})")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total ingredients in original file:     {total_count}")
    print(f"Successfully enriched:                   {enriched_count} ({enriched_count/total_count*100:.1f}%)")
    print(f"Not enriched (listed above):             {len(unmatched)} ({len(unmatched)/total_count*100:.1f}%)")
    print()

    # Additional breakdown by classification
    print("Breakdown by classification:")
    for classification in sorted(by_classification.keys()):
        count = len(by_classification[classification])
        print(f"  - {classification}: {count}")
    print()
    print("=" * 70)


def main():
    """Main execution function."""
    print("=" * 70)
    print("Diagnostic: Find Unmatched Ingredients")
    print("=" * 70)
    print()
    print(f"Original file:  {ORIGINAL_FILE}")
    print(f"Enriched file:  {ENRICHED_FILE}")
    print()

    # Check if files exist
    if not os.path.exists(ORIGINAL_FILE):
        print(f"ERROR: Original file not found: {ORIGINAL_FILE}")
        sys.exit(1)

    if not os.path.exists(ENRICHED_FILE):
        print(f"ERROR: Enriched file not found: {ENRICHED_FILE}")
        sys.exit(1)

    # Load both files
    print("Loading files...")
    original_data = load_json_file(ORIGINAL_FILE)
    enriched_data = load_json_file(ENRICHED_FILE)
    print("✓ Files loaded successfully")

    # Get total counts
    all_ingredients = original_data.get("entities", [])
    total_count = len(all_ingredients)
    print(f"✓ Found {total_count} total ingredients in original file")

    # Extract enriched IDs
    print("Analyzing enriched ingredients...")
    enriched_ids = get_enriched_ids(enriched_data)
    enriched_count = len(enriched_ids)
    print(f"✓ Found {enriched_count} enriched ingredients")

    # Find unmatched ingredients
    print("Identifying unmatched ingredients...")
    unmatched = find_unmatched_ingredients(original_data, enriched_ids)
    print(f"✓ Found {len(unmatched)} unmatched ingredients")

    # Print results
    print_results(unmatched, total_count, enriched_count)

    # Return exit code based on results
    if unmatched:
        print("ℹ️  To enrich these ingredients, add mappings to:")
        print("   backend/app/models/health_pillars.py (OUTCOME_TO_PILLARS dictionary)")
        print()
        sys.exit(0)  # Success, but with unmatched items
    else:
        print("🎉 All ingredients are enriched!")
        sys.exit(0)


if __name__ == "__main__":
    main()
