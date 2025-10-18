"""
Nutrition service utilities for energy expenditure and macronutrient goals.

This module implements Mifflin-St Jeor BMR, applies activity multipliers to
derive TDEE, and computes daily macro targets based on user goal profiles.
"""

from __future__ import annotations

from typing import Dict


_ACTIVITY_MULTIPLIERS: Dict[str, float] = {
    "sedentary": 1.2,
    "lightly active": 1.375,
    "moderately active": 1.55,
    "very active": 1.725,
    "extra active": 1.9,
}


_MACRO_SPLITS: Dict[str, Dict[str, float]] = {
    # Percent splits for daily calories
    # carbs/protein at 4 kcal/g, fat at 9 kcal/g
    "weight loss": {"carbs": 0.40, "protein": 0.30, "fat": 0.30},
    "maintain": {"carbs": 0.50, "protein": 0.20, "fat": 0.30},
    "muscle gain": {"carbs": 0.40, "protein": 0.35, "fat": 0.25},
}


def _normalize_gender(gender: str) -> str:
    return (gender or "").strip().lower()


def _normalize_activity(level: str) -> str:
    return (level or "").strip().lower()


def _normalize_goal_profile(goal_profile: str) -> str:
    return (goal_profile or "").strip().lower()


def calculate_tdee(
    *,
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    activity_level: str,
) -> float:
    """Calculate Total Daily Energy Expenditure using Mifflin-St Jeor.

    Args:
        weight_kg: Body weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: "male" or "female" (case-insensitive)
        activity_level: One of Sedentary/Lightly/Moderately/Very/Extra active

    Returns:
        Estimated TDEE in kcal/day (float)
    """
    if weight_kg is None or height_cm is None or age is None:
        raise ValueError("Missing required biometrics: weight_kg, height_cm, age")

    g = _normalize_gender(gender)
    if g not in {"male", "m", "man", "female", "f", "woman"}:
        raise ValueError("Unsupported gender; expected 'male' or 'female'")

    if g in {"male", "m", "man"}:
        bmr = (10.0 * float(weight_kg)) + (6.25 * float(height_cm)) - (5.0 * float(age)) + 5.0
    else:
        bmr = (10.0 * float(weight_kg)) + (6.25 * float(height_cm)) - (5.0 * float(age)) - 161.0

    level = _normalize_activity(activity_level)
    multiplier = _ACTIVITY_MULTIPLIERS.get(level)
    if multiplier is None:
        # Try to fuzzy match common variants
        # e.g., "light", "moderate", "very", "extra"
        if level.startswith("light"):
            multiplier = _ACTIVITY_MULTIPLIERS["lightly active"]
        elif level.startswith("moderate"):
            multiplier = _ACTIVITY_MULTIPLIERS["moderately active"]
        elif level.startswith("very"):
            multiplier = _ACTIVITY_MULTIPLIERS["very active"]
        elif level.startswith("extra"):
            multiplier = _ACTIVITY_MULTIPLIERS["extra active"]
        else:
            multiplier = _ACTIVITY_MULTIPLIERS["sedentary"]

    tdee = bmr * multiplier
    return float(round(tdee, 2))


def calculate_macronutrient_goals(*, tdee: float, goal_profile: str) -> Dict[str, float]:
    """Calculate macronutrient targets (grams) from TDEE and goal profile.

    Args:
        tdee: Total daily energy expenditure in kcal/day
        goal_profile: One of "Weight Loss", "Maintain", "Muscle Gain" (case-insensitive)

    Returns:
        Dict with keys: calories, protein_g, carbs_g, fat_g
    """
    profile_key = _normalize_goal_profile(goal_profile)
    splits = _MACRO_SPLITS.get(profile_key, _MACRO_SPLITS["maintain"])

    carb_calories = tdee * splits["carbs"]
    protein_calories = tdee * splits["protein"]
    fat_calories = tdee * splits["fat"]

    carbs_g = carb_calories / 4.0
    protein_g = protein_calories / 4.0
    fat_g = fat_calories / 9.0

    return {
        "calories": float(round(tdee, 2)),
        "protein_g": float(round(protein_g, 1)),
        "carbs_g": float(round(carbs_g, 1)),
        "fat_g": float(round(fat_g, 1)),
    }


