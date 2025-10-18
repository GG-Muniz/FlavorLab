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


# Initialize the async Anthropic client
settings = get_settings()
client = AsyncAnthropic(api_key=settings.anthropic_api_key)


def generate_meal_plan_prompt(survey_data: dict, num_days: int, include_recipes: bool, preferred_ingredients: Optional[List[str]] = None) -> str:
    """
    Generate a detailed prompt for the LLM to create a personalized meal plan.

    Args:
        survey_data: User's survey data including health pillars, dietary restrictions, etc.
        num_days: Number of days for the meal plan
        include_recipes: Whether to include detailed recipe information
        preferred_ingredients: Optional list of ingredient names to prioritize based on health goals

    Returns:
        str: Formatted prompt for the LLM
    """
    # Extract survey data
    health_pillars = survey_data.get("healthPillars", [])
    dietary_restrictions = survey_data.get("dietaryRestrictions", [])
    meal_complexity = survey_data.get("mealComplexity", "moderate")
    disliked_ingredients = survey_data.get("dislikedIngredients", [])
    meals_per_day = survey_data.get("mealsPerDay", "3-meals-2-snacks")
    allergies = survey_data.get("allergies", [])
    primary_goal = survey_data.get("primaryGoal", "")

    # Format allergies for critical constraint
    allergy_constraint = ""
    if allergies:
        allergy_list = ", ".join(allergies)
        allergy_constraint = f"""
## CRITICAL ALLERGY CONSTRAINT
The user has the following allergies: {allergy_list}
YOU MUST NEVER include these ingredients in any meal. This is a safety requirement.
Double-check every ingredient against this allergy list before including it.
"""

    # Determine meal structure
    meal_structure_map = {
        "3": "3 meals (breakfast, lunch, dinner)",
        "3-meals-2-snacks": "3 main meals (breakfast, lunch, dinner) + 2 snacks (morning snack, afternoon snack)",
        "6": "6 small meals throughout the day"
    }
    meal_structure = meal_structure_map.get(meals_per_day, "3 main meals + 2 snacks")

    # Conditional recipe details section
    recipe_section = ""
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

    # Preferred ingredients section
    preferred_ingredients_section = ""
    if preferred_ingredients:
        preferred_ingredients_section = f"""
## PREFERRED INGREDIENTS
Based on the user's health goals, prioritize using the following ingredients in the meal plan. You do not have to use all of them, but they should be featured prominently and creatively:
{', '.join(preferred_ingredients)}
"""

    # Build the complete prompt
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

[
  {{
    "day": "Day 1",
    "meals": [
      {{
        "type": "breakfast",
        "name": "Meal Name",
        "calories": 400,
        "description": "Brief description"{"," if include_recipes else ""}
        {"'ingredients': ['ingredient 1', 'ingredient 2']," if include_recipes else ""}
        {"'servings': 2," if include_recipes else ""}
        {"'prep_time_minutes': 10," if include_recipes else ""}
        {"'cook_time_minutes': 15," if include_recipes else ""}
        {"'instructions': ['step 1', 'step 2']," if include_recipes else ""}
        {"'nutrition': {'protein': '20g', 'carbs': '45g', 'fat': '12g'}" if include_recipes else ""}
      }}
    ]
  }}
]

Generate the {num_days}-day meal plan now as pure JSON:"""

    return prompt


async def generate_llm_meal_plan(
    user: User,
    num_days: int = 1,
    include_recipes: bool = False,
    db: Session = None
) -> List[DailyMealPlan]:
    """
    Generate a personalized meal plan using Claude Haiku LLM.

    Args:
        user: User model with preferences containing survey_data
        num_days: Number of days for the meal plan (default: 1)
        include_recipes: Whether to include detailed recipe information (default: False)
        db: Database session for fetching preferred ingredients (optional)

    Returns:
        List[DailyMealPlan]: Validated list of daily meal plans

    Raises:
        LLMResponseError: If LLM response cannot be parsed or validated
        ValueError: If user has no survey_data in preferences
    """
    try:
        # Retrieve survey data from user preferences
        if not user.preferences or "survey_data" not in user.preferences:
            raise ValueError("User has no survey data in preferences")

        survey_data = user.preferences["survey_data"]

        # Fetch preferred ingredients based on user health goals
        preferred_ingredient_names = []
        if db is not None:
            user_health_goals = user.preferences.get("health_goals", [])
            if user_health_goals:
                preferred_ingredients = []
                for pillar_id in user_health_goals:
                    try:
                        pillar_ingredients = IngredientEntity.get_ingredients_by_pillar(
                            db, pillar_id=pillar_id, limit=10
                        )
                        preferred_ingredients.extend(pillar_ingredients)
                    except Exception as e:
                        logger.warning(f"Could not fetch ingredients for pillar {pillar_id}: {e}")
                        continue

                # Deduplicate ingredients
                seen = set()
                unique_ingredients = [
                    ing for ing in preferred_ingredients
                    if not (ing.id in seen or seen.add(ing.id))
                ]

                # Extract ingredient names
                preferred_ingredient_names = [ing.name for ing in unique_ingredients]
                logger.info(f"Found {len(preferred_ingredient_names)} preferred ingredients for user {user.id}")

        # Generate the prompt
        prompt = generate_meal_plan_prompt(
            survey_data,
            num_days,
            include_recipes,
            preferred_ingredients=preferred_ingredient_names if preferred_ingredient_names else None
        )

        logger.info(f"Generating LLM meal plan for user {user.id} ({num_days} days, recipes={include_recipes})")

        # Make async API call to Claude Haiku
        message = await client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,  # Haiku's max token limit
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract the response content
        response_text = message.content[0].text.strip()
        logger.debug(f"LLM response: {response_text[:500]}...")

        # Parse JSON response
        try:
            meal_plan_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response text: {response_text}")
            raise LLMResponseError(f"LLM returned invalid JSON: {e}")

        # Validate against Pydantic model
        try:
            validated_plans = [DailyMealPlan.model_validate(day) for day in meal_plan_data]
            logger.info(f"Successfully generated and validated {len(validated_plans)} days")
            return validated_plans
        except ValidationError as e:
            logger.error(f"Failed to validate LLM response against schema: {e}")
            logger.error(f"Meal plan data: {meal_plan_data}")
            raise LLMResponseError(f"LLM response does not match expected schema: {e}")

    except (ValueError, LLMResponseError):
        # Re-raise expected errors
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error generating LLM meal plan: {e}")
        raise LLMResponseError(f"Failed to generate meal plan: {e}")
