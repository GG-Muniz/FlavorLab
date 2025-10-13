#!/usr/bin/env python3
"""
Test script for health_pillars.py module functionality.
Tests all helper functions to ensure proper pillar mapping and validation.
"""

import sys
sys.path.insert(0, '/home/holberton/FlavorLab/backend')

from app.models.health_pillars import (
    get_pillar_name,
    get_pillar_ids_for_outcome,
    validate_pillar_id,
    get_all_pillars,
    HEALTH_PILLARS
)

def test_get_pillar_name():
    """Test get_pillar_name function."""
    print("\n=== Testing get_pillar_name() ===")

    tests = [
        (1, "Increased Energy"),
        (8, "Inflammation Reduction"),
        (5, "Mental Clarity"),
        (99, None),
        (0, None),
    ]

    for pillar_id, expected in tests:
        result = get_pillar_name(pillar_id)
        status = "✓" if result == expected else "✗"
        print(f"{status} get_pillar_name({pillar_id}) = {result} (expected: {expected})")

def test_get_pillar_ids_for_outcome():
    """Test get_pillar_ids_for_outcome function."""
    print("\n=== Testing get_pillar_ids_for_outcome() ===")

    tests = [
        ("Inflammation", [8]),
        ("gut health", [2]),
        ("focus", [5]),
        ("Anti-inflammatory", [8]),
        ("energy", [1]),
        ("Supports digestion", [2]),
        ("immune", [3]),
        ("sleep quality", [4]),
        ("heart", [6]),
        ("muscle recovery", [7]),
        ("unknown outcome", []),
        ("", []),
    ]

    for outcome, expected in tests:
        result = get_pillar_ids_for_outcome(outcome)
        # Sort both for comparison
        result_sorted = sorted(result)
        expected_sorted = sorted(expected)
        status = "✓" if result_sorted == expected_sorted else "✗"
        print(f"{status} get_pillar_ids_for_outcome('{outcome}') = {result} (expected: {expected})")

def test_validate_pillar_id():
    """Test validate_pillar_id function."""
    print("\n=== Testing validate_pillar_id() ===")

    tests = [
        (1, True),
        (8, True),
        (5, True),
        (0, False),
        (9, False),
        (99, False),
        (-1, False),
    ]

    for pillar_id, expected in tests:
        result = validate_pillar_id(pillar_id)
        status = "✓" if result == expected else "✗"
        print(f"{status} validate_pillar_id({pillar_id}) = {result} (expected: {expected})")

def test_get_all_pillars():
    """Test get_all_pillars function."""
    print("\n=== Testing get_all_pillars() ===")

    pillars = get_all_pillars()

    # Check length
    if len(pillars) == 8:
        print(f"✓ get_all_pillars() returned 8 pillars")
    else:
        print(f"✗ get_all_pillars() returned {len(pillars)} pillars (expected: 8)")

    # Check structure of first pillar
    if pillars:
        first = pillars[0]
        has_id = "id" in first
        has_name = "name" in first
        has_description = "description" in first

        if has_id and has_name and has_description:
            print(f"✓ Pillar structure is correct")
            print(f"  Example: {first}")
        else:
            print(f"✗ Pillar structure is incorrect")
            print(f"  Has id: {has_id}, Has name: {has_name}, Has description: {has_description}")

    # Verify all IDs are 1-8
    ids = [p["id"] for p in pillars]
    if ids == list(range(1, 9)):
        print(f"✓ All pillar IDs are 1-8 in correct order")
    else:
        print(f"✗ Pillar IDs are incorrect: {ids}")

def test_health_pillars_constant():
    """Test HEALTH_PILLARS constant."""
    print("\n=== Testing HEALTH_PILLARS Constant ===")

    expected_names = [
        "Increased Energy",
        "Improved Digestion",
        "Enhanced Immunity",
        "Better Sleep",
        "Mental Clarity",
        "Heart Health",
        "Muscle Recovery",
        "Inflammation Reduction"
    ]

    for pillar_id in range(1, 9):
        if pillar_id in HEALTH_PILLARS:
            name = HEALTH_PILLARS[pillar_id]["name"]
            expected = expected_names[pillar_id - 1]
            status = "✓" if name == expected else "✗"
            print(f"{status} HEALTH_PILLARS[{pillar_id}]['name'] = '{name}' (expected: '{expected}')")
        else:
            print(f"✗ HEALTH_PILLARS[{pillar_id}] is missing")

if __name__ == "__main__":
    print("=" * 60)
    print("HEALTH PILLAR MODULE TESTS")
    print("=" * 60)

    test_get_pillar_name()
    test_get_pillar_ids_for_outcome()
    test_validate_pillar_id()
    test_get_all_pillars()
    test_health_pillars_constant()

    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)
