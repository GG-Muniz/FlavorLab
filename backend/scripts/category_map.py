"""
Lightweight category mapping for ingredients.

This file provides simple heuristics to assign ingredients to categories
using exact-name and substring rules. Slugs here must match seeded
category slugs (see scripts/seed_categories.py).
"""

from typing import Dict, List

# Exact matches (case-sensitive names from the database) → list of category slugs
NAME_TO_CATEGORY_SLUGS: Dict[str, List[str]] = {
    # Fruits/Berries
    "Blueberries": ["fruits", "berries"],
    "Elderberries": ["fruits", "berries"],
    "Mixed Berries": ["fruits", "berries"],

    # Vegetables / Alliums
    "Garlic": ["vegetables", "alliums"],
    "Broccoli": ["vegetables"],

    # Juices / Beverages
    "Tart Cherry Juice": ["juices"],
    "Beet Juice": ["juices"],
    "Coffee": ["beverages", "tea-coffee"],
    "Green Tea": ["beverages", "tea-coffee"],
    "Bone Broth": ["beverages", "broths"],

    # Dairy / Fermented
    "Greek Yogurt": ["dairy"],
    "Yogurt": ["dairy"],
    "Cottage Cheese": ["dairy"],
    "Milk": ["dairy"],
    "Kefir": ["dairy", "fermented"],

    # Seafood / Meats
    "Salmon": ["seafood"],
    "Wild Salmon": ["seafood"],
    "Fatty Fish": ["seafood"],
    "Tuna": ["seafood"],

    # Fermented / Vegetables
    "Sauerkraut": ["fermented", "vegetables"],
}


# Heuristic substring rules (lowercase contains) → category slug
# If a name contains any of these substrings, that category slug is added.
SUBSTRING_RULES: Dict[str, List[str]] = {
    "berries": ["berry", "berries"],
    "juices": ["juice"],
    "seafood": ["salmon", "tuna", "sardine", "mackerel", "trout", "fish"],
    "dairy": ["yogurt", "yoghurt", "milk", "cheese", "kefir", "cream"],
    "fermented": ["sauerkraut", "kimchi", "kombucha", "kefir", "miso", "tempeh"],
    "broths": ["broth", "stock"],
    "alliums": ["garlic", "onion", "leek", "shallot", "chive"],
}


# Optional mapping from free-form classifications (if present) → category slug
CLASSIFICATION_TO_CATEGORY_SLUGS: Dict[str, str] = {
    "fruits": "fruits",
    "fruit": "fruits",
    "berries": "berries",
    "vegetables": "vegetables",
    "veg": "vegetables",
    "leafy greens": "leafy-greens",
    "juices": "juices",
    "juice": "juices",
    "dairy": "dairy",
    "seafood": "seafood",
    "meats": "meats",
    "nuts seeds": "nuts-seeds",
    "nuts & seeds": "nuts-seeds",
    "herbs spices": "herbs-spices",
    "herbs & spices": "herbs-spices",
}


