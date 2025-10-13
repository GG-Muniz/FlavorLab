"""
Health Pillar System for FlavorLab.

This module defines the 8 core health pillars used throughout the application
for ingredient classification, user health goals, and meal plan generation.
It provides centralized constants and helper functions for working with health pillars.
"""

from typing import List, Dict, Any, Optional


# Core health pillar definitions
# Maps pillar IDs (1-8) to structured data including name and description
HEALTH_PILLARS: Dict[int, Dict[str, str]] = {
    1: {
        "name": "Increased Energy",
        "description": "Supports sustained energy levels and reduces fatigue"
    },
    2: {
        "name": "Improved Digestion",
        "description": "Promotes healthy digestive function and gut health"
    },
    3: {
        "name": "Enhanced Immunity",
        "description": "Strengthens immune system and resilience"
    },
    4: {
        "name": "Better Sleep",
        "description": "Supports quality sleep and rest"
    },
    5: {
        "name": "Mental Clarity",
        "description": "Enhances focus, cognitive function, and brain health"
    },
    6: {
        "name": "Heart Health",
        "description": "Supports cardiovascular health and circulation"
    },
    7: {
        "name": "Muscle Recovery",
        "description": "Aids muscle recovery, strength, and athletic performance"
    },
    8: {
        "name": "Inflammation Reduction",
        "description": "Reduces inflammation and supports anti-inflammatory processes"
    }
}


# Mapping from health outcome strings to pillar IDs
# Keys are lowercase for case-insensitive matching
# Values are lists of pillar IDs that the outcome maps to
OUTCOME_TO_PILLARS: Dict[str, List[int]] = {
    # Energy-related outcomes (Pillar 1)
    "energy": [1],
    "vitality": [1],
    "stamina": [1],
    "fatigue": [1],
    "endurance": [1],

    # Digestion-related outcomes (Pillar 2)
    "digestion": [2],
    "digestive": [2],
    "gut health": [2],
    "gut": [2],
    "bloating": [2],
    "intestinal": [2],
    "digestive health": [2],
    "gastrointestinal": [2],

    # Immunity-related outcomes (Pillar 3)
    "immunity": [3],
    "immune": [3],
    "immune support": [3],
    "immune system": [3],
    "resilience": [3],
    "immune function": [3],
    "immune response": [3],

    # Sleep-related outcomes (Pillar 4)
    "sleep": [4],
    "rest": [4],
    "insomnia": [4],
    "sleep quality": [4],
    "sleep support": [4],
    "restful": [4],

    # Mental/cognitive outcomes (Pillar 5)
    "mental": [5],
    "mental clarity": [5],
    "focus": [5],
    "cognitive": [5],
    "brain health": [5],
    "clarity": [5],
    "concentration": [5],
    "memory": [5],
    "brain function": [5],
    "cognitive function": [5],

    # Heart health outcomes (Pillar 6)
    "heart": [6],
    "heart health": [6],
    "cardiovascular": [6],
    "cholesterol": [6],
    "blood pressure": [6],
    "circulation": [6],
    "cardiac": [6],

    # Muscle/recovery outcomes (Pillar 7)
    "muscle": [7],
    "muscle recovery": [7],
    "recovery": [7],
    "strength": [7],
    "athletic": [7],
    "athletic performance": [7],
    "performance": [7],
    "muscle building": [7],
    "exercise": [7],

    # Inflammation-related outcomes (Pillar 8)
    "inflammation": [8],
    "anti-inflammatory": [8],
    "inflammatory": [8],
    "reduce inflammation": [8],
    "inflammation reduction": [8],

    # Common ingredients mapped to health pillars
    # Anti-inflammatory ingredients (Pillar 8)
    "turmeric": [8],
    "ginger": [2, 8],  # Digestion + Anti-inflammatory
    "garlic": [3, 6, 8],  # Immunity + Heart + Anti-inflammatory
    "olive oil": [6, 8],  # Heart + Anti-inflammatory
    "salmon": [6, 7, 8],  # Heart + Muscle + Anti-inflammatory
    "fatty fish": [6, 7, 8],
    "tuna": [6, 7],
    "walnuts": [5, 6, 8],  # Mental + Heart + Anti-inflammatory
    "almonds": [6, 7],  # Heart + Muscle
    "blueberries": [3, 5, 8],  # Immunity + Mental + Anti-inflammatory
    "berries": [3, 5, 8],
    "elderberries": [3],  # Immunity
    "cherries": [4, 8],  # Sleep + Anti-inflammatory
    "tart cherries": [4, 7, 8],  # Sleep + Muscle + Anti-inflammatory
    "dark chocolate": [5, 6],  # Mental + Heart
    "green tea": [5, 6, 8],  # Mental + Heart + Anti-inflammatory
    "coffee": [1, 5],  # Energy + Mental

    # Probiotic/digestive ingredients (Pillar 2)
    "yogurt": [2, 7],  # Digestion + Muscle
    "greek yogurt": [2, 7],
    "kefir": [2, 3],  # Digestion + Immunity
    "sauerkraut": [2, 3],
    "bone broth": [2, 7, 8],  # Digestion + Muscle + Anti-inflammatory

    # Energy/nutrient-dense ingredients (Pillar 1)
    "oats": [1, 2, 6],  # Energy + Digestion + Heart
    "quinoa": [1, 7],  # Energy + Muscle
    "sweet potato": [1, 2],  # Energy + Digestion
    "bananas": [1, 4],  # Energy + Sleep
    "eggs": [1, 5, 7],  # Energy + Mental + Muscle
    "spinach": [1, 3, 6],  # Energy + Immunity + Heart
    "lentils": [1, 2, 6],  # Energy + Digestion + Heart
    "beans": [1, 2, 6],
    "legumes": [1, 2, 6],

    # Sleep-supporting ingredients (Pillar 4)
    "chamomile": [4],  # Sleep
    "passionflower": [4],
    "kiwi": [3, 4],  # Immunity + Sleep

    # Mental clarity/brain health (Pillar 5)
    "avocado": [5, 6],  # Mental + Heart
    "beef liver": [1, 5, 7],  # Energy + Mental + Muscle

    # Heart health (Pillar 6)
    "beets": [1, 6, 7],  # Energy + Heart + Muscle
    "beet juice": [1, 6, 7],
    "pomegranate": [6, 8],  # Heart + Anti-inflammatory
    "citrus": [3, 6],  # Immunity + Heart
    "oranges": [3, 6],
    "tomatoes": [6, 8],  # Heart + Anti-inflammatory

    # Muscle recovery (Pillar 7)
    "chicken": [7],  # Muscle
    "turkey": [4, 7],  # Sleep + Muscle
    "poultry": [7],  # Muscle (general category)
    "cottage cheese": [4, 7],  # Sleep + Muscle
    "milk": [4, 7],  # Sleep + Muscle

    # Immunity boosters (Pillar 3)
    "broccoli": [2, 3, 8],  # Digestion + Immunity + Anti-inflammatory
    "mushrooms": [3, 7],  # Immunity + Muscle
    "shiitake": [3, 7],
    "pumpkin seeds": [3, 7],  # Immunity + Muscle
    "sunflower seeds": [3, 6],  # Immunity + Heart

    # Multi-benefit ingredients
    "chia seeds": [1, 2, 6],  # Energy + Digestion + Heart
    "flax seeds": [2, 6, 8],  # Digestion + Heart + Anti-inflammatory
    "peppermint": [2],  # Digestion
    "fennel": [2],  # Digestion
    "honey": [1, 3, 4],  # Energy + Immunity + Sleep
    "pineapple": [2, 8],  # Digestion + Anti-inflammatory
    "papaya": [2],  # Digestion
    "watermelon": [1, 6],  # Energy + Heart

    # Priority ingredients - previously unmatched
    "apple": [2, 6],  # Digestion (fiber) + Heart (quercetin, pectin)
    "apples": [2, 6],
    "artichoke": [2, 6],  # Digestion + Heart (cynarin supports liver/digestion)
    "brown rice": [1, 2, 6],  # Energy + Digestion (fiber) + Heart
    "rice": [1, 2, 6],
    "dark leafy greens": [1, 3, 6, 8],  # Energy (iron) + Immunity + Heart + Anti-inflammatory
    "leafy greens": [1, 3, 6, 8],
    "kale": [1, 3, 6, 8],  # Energy + Immunity + Heart + Anti-inflammatory
    "nuts": [5, 6, 7],  # Mental + Heart + Muscle (healthy fats, protein)
    "mixed nuts": [5, 6, 7],
    "almond": [6, 7],  # Heart + Muscle (already mapped above, added for consistency)
    "walnut": [5, 6, 8],  # Mental + Heart + Anti-inflammatory (already mapped above)
    "oyster": [3, 5, 7],  # Immunity (zinc) + Mental + Muscle
    "oysters": [3, 5, 7],
    "red bell pepper": [3, 6],  # Immunity (vitamin C) + Heart (antioxidants)
    "bell pepper": [3, 6],
    "red pepper": [3, 6],
    "shellfish": [3, 5, 7],  # Immunity (zinc, selenium) + Mental (B12) + Muscle (protein)
    "shrimp": [3, 5, 7],
    "tart cherry juice": [4, 7, 8],  # Sleep (melatonin) + Muscle + Anti-inflammatory
    "cherry juice": [4, 7, 8],
    "whole grain": [1, 2, 6],  # Energy + Digestion (fiber) + Heart
    "whole grains": [1, 2, 6],
    "grain": [1, 2],
}


def get_pillar_name(pillar_id: int) -> Optional[str]:
    """
    Get the name of a health pillar by its ID.

    Args:
        pillar_id: Integer ID of the pillar (1-8)

    Returns:
        The pillar name if found, None otherwise

    Example:
        >>> get_pillar_name(1)
        'Increased Energy'
        >>> get_pillar_name(99)
        None
    """
    pillar = HEALTH_PILLARS.get(pillar_id)
    return pillar["name"] if pillar else None


def get_pillar_ids_for_outcome(outcome_string: str) -> List[int]:
    """
    Map a health outcome string to corresponding health pillar IDs.

    This function performs case-insensitive matching and supports partial matches.
    It checks if any of the known outcome keywords appear in the input string.

    Args:
        outcome_string: Raw health outcome string (e.g., "Anti-inflammatory",
                       "Supports digestion", "Boosts immunity")

    Returns:
        List of pillar IDs that match the outcome. Returns empty list if no matches.
        May return multiple IDs if the outcome maps to multiple pillars.

    Example:
        >>> get_pillar_ids_for_outcome("Anti-inflammatory")
        [8]
        >>> get_pillar_ids_for_outcome("Supports gut health")
        [2]
        >>> get_pillar_ids_for_outcome("Unknown outcome")
        []
    """
    if not outcome_string:
        return []

    # Convert to lowercase for case-insensitive matching
    outcome_lower = outcome_string.lower()

    # Collect all matching pillar IDs
    matching_pillars = set()

    # Check for exact matches first
    if outcome_lower in OUTCOME_TO_PILLARS:
        matching_pillars.update(OUTCOME_TO_PILLARS[outcome_lower])

    # Check for partial matches (substring matching)
    # This allows matching "Supports digestion" to "digestion"
    for outcome_key, pillar_ids in OUTCOME_TO_PILLARS.items():
        if outcome_key in outcome_lower:
            matching_pillars.update(pillar_ids)

    return sorted(list(matching_pillars))


def validate_pillar_id(pillar_id: int) -> bool:
    """
    Validate that a pillar ID is in the valid range (1-8).

    Args:
        pillar_id: Integer to validate

    Returns:
        True if the ID is valid, False otherwise

    Example:
        >>> validate_pillar_id(5)
        True
        >>> validate_pillar_id(0)
        False
        >>> validate_pillar_id(9)
        False
    """
    return pillar_id in HEALTH_PILLARS


def get_all_pillars() -> List[Dict[str, Any]]:
    """
    Get a list of all health pillars with their complete data.

    Returns:
        List of dictionaries, each containing:
        - id: Pillar ID (1-8)
        - name: Pillar name
        - description: Pillar description

    Example:
        >>> pillars = get_all_pillars()
        >>> len(pillars)
        8
        >>> pillars[0]
        {'id': 1, 'name': 'Increased Energy', 'description': '...'}
    """
    return [
        {
            "id": pillar_id,
            "name": data["name"],
            "description": data["description"]
        }
        for pillar_id, data in sorted(HEALTH_PILLARS.items())
    ]


# Convenience constant for quick validation
VALID_PILLAR_IDS = set(HEALTH_PILLARS.keys())
