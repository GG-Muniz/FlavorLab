"""
LLM service for generating personalized meal plans using Claude Haiku.

This module provides functionality to interact with the Anthropic Claude API
to generate AI-powered meal plans based on user survey data and preferences.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic
from pydantic import ValidationError
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models.user import User
from ..models.entity import IngredientEntity
from ..models.health_pillars import HEALTH_PILLARS, get_pillar_name
from ..schemas.meal_plan import DailyMealPlan

logger = logging.getLogger(__name__)


class LLMResponseError(Exception):
    """Exception raised when LLM response cannot be parsed or validated."""

    pass


settings = get_settings()
logger.info("[LLM DEBUG] Loading Anthropic API key from settings...")
logger.info(f"[LLM DEBUG] API key present: {bool(settings.anthropic_api_key)}")
logger.info(
    f"[LLM DEBUG] API key prefix: {settings.anthropic_api_key[:20] if settings.anthropic_api_key else 'NONE'}..."
)
client = AsyncAnthropic(api_key=settings.anthropic_api_key)


def generate_meal_plan_prompt(
    survey_data: dict,
    num_days: int,
    include_recipes: bool,
    preferred_ingredients: Optional[List[str]] = None,
) -> str:
    health_pillars = survey_data.get("healthPillars", [])
    dietary_restrictions = survey_data.get("dietaryRestrictions", [])
    meal_complexity = survey_data.get("mealComplexity", "moderate")
    disliked_ingredients = survey_data.get("dislikedIngredients", [])
    meals_per_day = survey_data.get("mealsPerDay", "3-meals-2-snacks")
    allergies = survey_data.get("allergies", [])
    primary_goal = survey_data.get("primaryGoal", "")

    allergy_constraint = ""
    if allergies:
        allergy_list = ", ".join(allergies)
        allergy_constraint = f"""
## CRITICAL ALLERGY CONSTRAINT
The user has the following allergies: {allergy_list}
YOU MUST NEVER include these ingredients in any meal. This is a safety requirement.
Double-check every ingredient against this allergy list before including it.
"""

    meal_structure_map = {
        "3": "3 meals (breakfast, lunch, dinner)",
        "3-meals-2-snacks": "3 main meals (breakfast, lunch, dinner) + 2 snacks (morning snack, afternoon snack)",
        "6": "6 small meals throughout the day",
    }
    meal_structure = meal_structure_map.get(meals_per_day, "3 main meals + 2 snacks")

    if include_recipes:
        recipe_section = """
For each meal, include:
- "ingredients": Array of ingredients with measurements (e.g., ["2 cups oats", "1 banana"])
- "servings": Number of servings (integer)
- "prep_time_minutes": Preparation time in minutes (integer)
- "cook_time_minutes": Cooking time in minutes (integer)
- "instructions": Array of step-by-step cooking instructions
- "nutrition": Object with detailed nutritional info (e.g., {"protein": "25g", "carbs": "40g", "fat": "15g", "fiber": "8g"})
"""
    else:
        recipe_section = """
For each meal, only include the basic fields (type, name, calories, description).
DO NOT include ingredients, servings, prep_time_minutes, cook_time_minutes, instructions, or nutrition fields.
"""

    preferred_ingredients_section = ""
    if preferred_ingredients:
        preferred_ingredients_section = f"""
## PREFERRED INGREDIENTS
Based on the user's health goals, prioritize using the following ingredients in the meal plan. You do not have to use all of them, but they should be featured prominently and creatively:
{', '.join(preferred_ingredients)}
"""

    example_day = {
        "day": "Day 1",
        "meals": [
            {
                "type": "breakfast",
                "name": "Meal Name",
                "calories": 400,
                "description": "Brief description",
            }
        ],
    }
    if include_recipes:
        example_day["meals"][0].update(
            {
                "ingredients": ["ingredient 1", "ingredient 2"],
                "servings": 2,
                "prep_time_minutes": 10,
                "cook_time_minutes": 15,
                "instructions": ["step 1", "step 2"],
                "nutrition": {"protein": "20g", "carbs": "45g", "fat": "12g"},
            }
        )
    example_json = json.dumps([example_day], indent=2)

    prompt = f"""You are FlavorLab's expert nutritionist and meal planning AI. Create a personalized {num_days}-day meal plan.
{allergy_constraint}
## DAILY MEAL STRUCTURE MANDATE
Each day MUST have exactly this structure: {meal_structure}

## USER PROFILE
- Health Goals: {', '.join(health_pillars)}
- Primary Goal: {primary_goal}
- Dietary Restrictions: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}
- Meal Complexity: {meal_complexity}
- Disliked Ingredients: {', '.join(disliked_ingredients) if disliked_ingredients else 'None'}
{preferred_ingredients_section}
## REQUIREMENTS
1. Address all health goals through food choices
2. Respect all dietary restrictions strictly
3. Avoid all disliked ingredients
4. Match the specified meal complexity level
5. Each day must follow the meal structure: {meal_structure}
{recipe_section}

## JSON-ONLY MANDATE
Respond ONLY with a JSON array. No markdown, no explanations, no code blocks.
The JSON must be a valid array that matches this schema:

{example_json}

Generate the {num_days}-day meal plan now as pure JSON:"""

    return prompt


def _resolve_user_preferences(user: User) -> Dict[str, Any]:
    if isinstance(user.preferences, str):
        try:
            return json.loads(user.preferences) if user.preferences else {}
        except json.JSONDecodeError:
            logger.warning("User %s preferences JSON decode failed; defaulting to empty dict", user.id)
            return {}
    return user.preferences or {}


async def generate_llm_meal_plan(
    user: User,
    num_days: int = 1,
    include_recipes: bool = False,
    db: Session = None,
) -> List[DailyMealPlan]:
    try:
        preferences = _resolve_user_preferences(user)
        if not preferences or "survey_data" not in preferences:
            raise ValueError("User has no survey data in preferences")

        survey_data = preferences["survey_data"]

        preferred_ingredient_names: List[str] = []
        if db is not None:
            user_health_goals = preferences.get("health_goals", [])
            if user_health_goals:
                preferred_ingredients = []
                for pillar_id in user_health_goals:
                    try:
                        pillar_ingredients = IngredientEntity.get_ingredients_by_pillar(db, pillar_id=pillar_id, limit=10)
                        preferred_ingredients.extend(pillar_ingredients)
                    except Exception as exc:
                        logger.warning("Could not fetch ingredients for pillar %s: %s", pillar_id, exc)
                        continue

                seen = set()
                unique_ingredients = [
                    ingredient
                    for ingredient in preferred_ingredients
                    if not (ingredient.id in seen or seen.add(ingredient.id))
                ]
                preferred_ingredient_names = [ingredient.name for ingredient in unique_ingredients]
                logger.info(
                    "Found %s preferred ingredients for user %s",
                    len(preferred_ingredient_names),
                    user.id,
                )

        prompt = generate_meal_plan_prompt(
            survey_data,
            num_days,
            include_recipes,
            preferred_ingredients=preferred_ingredient_names if preferred_ingredient_names else None,
        )

        logger.info(
            "Generating LLM meal plan for user %s (%s days, recipes=%s)",
            user.id,
            num_days,
            include_recipes,
        )
        logger.info("[LLM DEBUG] Prompt length: %s chars", len(prompt))

        try:
            logger.info("[LLM DEBUG] Calling Anthropic API with model: claude-3-haiku-20240307")
            message = await client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            logger.info("[LLM DEBUG] API call successful!")
        except Exception as api_error:
            logger.error("[LLM DEBUG] Anthropic API call failed: %s: %s", type(api_error).__name__, api_error)
            raise

        response_text = message.content[0].text.strip()
        logger.debug("LLM response: %s...", response_text[:500])

        try:
            meal_plan_data = json.loads(response_text)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse LLM response as JSON: %s", exc)
            logger.error("Response text: %s", response_text)
            raise LLMResponseError(f"LLM returned invalid JSON: {exc}")

        try:
            validated_plans = [DailyMealPlan.model_validate(day) for day in meal_plan_data]
            logger.info("Successfully generated and validated %s days", len(validated_plans))
            return validated_plans
        except ValidationError as exc:
            logger.error("Failed to validate LLM response against schema: %s", exc)
            logger.error("Meal plan data: %s", meal_plan_data)
            raise LLMResponseError(f"LLM response does not match expected schema: {exc}")
    except (ValueError, LLMResponseError):
        raise
    except Exception as exc:
        logger.error("Unexpected error generating LLM meal plan: %s", exc)
        raise LLMResponseError(f"Failed to generate meal plan: {exc}")
