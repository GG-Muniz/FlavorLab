"""
LLM Service for FlavorLab Meal Plan Generation.

This module provides integration with Anthropic's Claude Haiku model
for AI-powered, personalized meal plan generation based on user survey data.
"""

import json
import logging
from typing import List, Dict, Any
from anthropic import AsyncAnthropic
from pydantic import ValidationError

from ..config import get_settings
from ..models.user import User
from ..schemas.meal_plan import DailyMealPlan
from fastapi import HTTPException, status

# Configure logging
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


class LLMResponseError(Exception):
    """Custom exception for LLM response parsing or validation errors."""
    pass


def generate_meal_plan_prompt(survey_data: dict, num_days: int, include_recipes: bool = False) -> str:
    """
    Generate a comprehensive system prompt for Claude Haiku to create meal plans.

    This prompt is designed to be extremely clear and direct, emphasizing:
    - JSON-only response (no markdown, no explanations)
    - CRITICAL allergy safety with derivative awareness
    - Strict adherence to dietary restrictions
    - Explicit daily meal structure enforcement
    - Optional detailed recipe generation
    - Personalization based on user survey data

    Args:
        survey_data: User's complete survey data from onboarding
        num_days: Number of days for the meal plan
        include_recipes: If True, generate detailed recipes with ingredients and instructions

    Returns:
        str: Formatted system prompt for Claude Haiku
    """

    # Extract user preferences
    health_pillars = survey_data.get("healthPillars", [])
    dietary_restrictions = survey_data.get("dietaryRestrictions", [])
    allergies = survey_data.get("allergies", [])
    disliked_ingredients = survey_data.get("dislikedIngredients", [])
    meal_complexity = survey_data.get("mealComplexity", "moderate")
    meals_per_day = survey_data.get("mealsPerDay", "3")
    primary_goal = survey_data.get("primaryGoal", "")

    # Build meal structure guidance
    meal_structure_guidance = _get_meal_structure_guidance(meals_per_day)

    # Build allergy warning with derivatives
    allergy_warning = _get_allergy_warning(allergies)

    prompt = f"""You are a world-class nutritionist and chef. Your sole purpose is to generate a structured meal plan in JSON format.

USER PROFILE:
- Health Goals: {', '.join(health_pillars) if health_pillars else 'General wellness'}
- Primary Goal: {primary_goal if primary_goal else 'General wellness'}
- Dietary Restrictions: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}
- Food Allergies: {', '.join(allergies) if allergies else 'None'}
- Disliked Ingredients: {', '.join(disliked_ingredients) if disliked_ingredients else 'None'}
- Preferred Meal Complexity: {meal_complexity}
- Daily Meal Structure: {meals_per_day}

⚠️ CRITICAL SAFETY CONSTRAINTS - READ CAREFULLY ⚠️

{allergy_warning}

DIETARY RESTRICTIONS ARE STRICT FILTERS:
You MUST strictly adhere to all dietary restrictions:
- Vegetarian = NO meat, poultry, or fish (eggs and dairy are OK)
- Vegan = NO animal products whatsoever (no meat, dairy, eggs, honey)
- Gluten-free = NO wheat, barley, rye, or their derivatives
- If no restrictions listed, all foods are allowed

DISLIKED INGREDIENTS:
Avoid these ingredients whenever possible: {', '.join(disliked_ingredients) if disliked_ingredients else 'None'}
These are preferences, not safety requirements.

🚨 MANDATORY DAILY MEAL STRUCTURE - CRITICAL REQUIREMENT 🚨
{meal_structure_guidance}

⚠️ THIS IS NON-NEGOTIABLE: You MUST follow the exact meal count and structure specified above for EVERY day.
Your response will be INVALID if the meal count does not match the requirement.

MEAL PLAN REQUIREMENTS:
- Generate exactly {num_days} days of meals
- CRITICAL: Follow the exact meal structure above (this is the most important requirement)
- Tailor meals to support the user's health goals: {', '.join(health_pillars) if health_pillars else 'general wellness'}
- Use {meal_complexity} complexity recipes
- Provide balanced nutrition across all meals
- Include accurate calorie estimates for each meal

RECIPE DETAIL LEVEL:
{'- INCLUDE FULL RECIPES: Generate detailed ingredients lists, servings, prep/cook times, step-by-step instructions, and nutrition info for each meal' if include_recipes else '- OVERVIEW MODE ONLY: Include ONLY the required fields (type, name, calories, description). DO NOT include ingredients, servings, prep_time_minutes, cook_time_minutes, instructions, or nutrition fields.'}

JSON RESPONSE FORMAT:
You MUST respond with ONLY a valid JSON array. Do not include any introductory text, explanations, or markdown formatting like ```json. Your entire response must be the JSON array itself.

{'⚠️ CRITICAL: The example below shows the EXACT fields required. DO NOT add any additional fields beyond what is shown. Do not include ingredients, instructions, servings, prep_time_minutes, cook_time_minutes, or nutrition unless explicitly shown in the example below.' if not include_recipes else '✅ Include all recipe details as shown in the example below.'}

The JSON must conform to this EXACT structure (match the fields shown):

{_get_json_example(include_recipes, meals_per_day)}

IMPORTANT REMINDERS:
- Your response must be ONLY the JSON array, starting with [ and ending with ]
- No text before or after the JSON
- No markdown code blocks
- No explanations or commentary
- 🚨 CRITICAL #1: Follow the EXACT daily meal structure (check the meal count!)
- 🚨 CRITICAL #2: Double-check for allergens and their derivatives
- Strictly follow all dietary restrictions
- Make meals appealing, nutritious, and aligned with user goals

BEFORE RESPONDING:
1. Count how many meals/snacks are required per day
2. Verify each day has the EXACT count specified
3. Verify meal types match the structure (e.g., if 2 snacks required, include 2 items with type "snack")

Generate the meal plan now:"""

    return prompt


def _get_meal_structure_guidance(meals_per_day: str) -> str:
    """Generate specific meal structure guidance based on user preference."""

    # Normalize the meals_per_day value
    mpd_lower = meals_per_day.lower().strip()

    if '3' in mpd_lower and 'snack' not in mpd_lower:
        return """The user wants 3 MEALS per day with NO snacks.
You MUST generate EXACTLY 3 meals each day with these types:
- "breakfast" (morning meal)
- "lunch" (midday meal)
- "dinner" (evening meal)
Do NOT include any meals with type "snack"."""

    elif '3' in mpd_lower and '2' in mpd_lower and 'snack' in mpd_lower:
        return """The user wants 3 MEALS + 2 SNACKS per day (5 items total).
🚨 MANDATORY: Each day MUST have EXACTLY 5 items in the "meals" array.
You MUST generate these types in this order:
1. type: "breakfast" (morning meal)
2. type: "snack" (morning snack)
3. type: "lunch" (midday meal)
4. type: "snack" (afternoon snack)
5. type: "dinner" (evening meal)

EXAMPLE STRUCTURE (you must follow this):
"meals": [
  {"type": "breakfast", "name": "...", ...},
  {"type": "snack", "name": "...", ...},
  {"type": "lunch", "name": "...", ...},
  {"type": "snack", "name": "...", ...},
  {"type": "dinner", "name": "...", ...}
]"""

    elif '5' in mpd_lower or ('4' in mpd_lower and 'snack' in mpd_lower):
        return """The user wants 5 EATING OCCASIONS per day.
You MUST generate EXACTLY 5 items each day with appropriate types:
- Mix of "breakfast", "lunch", "dinner", and "snack" types
- Ensure balanced distribution throughout the day"""

    elif '6' in mpd_lower:
        return """The user wants 6 SMALLER MEALS per day.
You MUST generate EXACTLY 6 eating occasions each day.
Use types like: "breakfast", "snack", "lunch", "snack", "dinner", "snack"
Or use: "meal1", "meal2", "meal3", "meal4", "meal5", "meal6"
Ensure portions are smaller since there are more frequent meals."""

    else:
        # Default fallback
        return f"""The user's desired structure is: {meals_per_day}
Generate the appropriate number of meals/snacks per day based on this preference."""


def _get_allergy_warning(allergies: list) -> str:
    """Generate emphatic allergy warning with derivative examples."""

    if not allergies:
        return "ALLERGIES: None listed. All ingredients are safe to use."

    # Build allergy warning with common derivatives
    allergy_derivatives = {
        'peanut': ['peanuts', 'peanut butter', 'peanut oil', 'peanut flour'],
        'peanuts': ['peanuts', 'peanut butter', 'peanut oil', 'peanut flour'],
        'soy': ['soy', 'tofu', 'edamame', 'soy sauce', 'soy milk', 'tempeh', 'miso'],
        'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'whey', 'casein'],
        'milk': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'whey', 'casein'],
        'egg': ['eggs', 'egg whites', 'egg yolks', 'mayonnaise'],
        'eggs': ['eggs', 'egg whites', 'egg yolks', 'mayonnaise'],
        'tree nut': ['almonds', 'walnuts', 'cashews', 'pecans', 'pistachios', 'almond butter'],
        'shellfish': ['shrimp', 'crab', 'lobster', 'prawns', 'crayfish'],
        'fish': ['salmon', 'tuna', 'cod', 'fish sauce', 'anchovies'],
        'wheat': ['wheat', 'flour', 'bread', 'pasta', 'couscous', 'seitan'],
        'gluten': ['wheat', 'barley', 'rye', 'flour', 'bread', 'pasta'],
    }

    warning = "🚨 ALLERGIES - CRITICAL SAFETY REQUIREMENT 🚨\n"
    warning += "You MUST NOT include ANY of these allergens OR their derivatives:\n\n"

    for allergen in allergies:
        allergen_lower = allergen.lower().strip()
        warning += f"❌ {allergen.upper()}: "

        # Find matching derivatives
        derivatives_found = False
        for key, derivatives in allergy_derivatives.items():
            if key in allergen_lower:
                warning += f"Forbidden ingredients include {', '.join(derivatives)}\n"
                derivatives_found = True
                break

        if not derivatives_found:
            warning += f"Avoid this ingredient and all its forms/derivatives\n"

    warning += "\n⚠️ BEFORE FINALIZING: Review EVERY ingredient in your meal plan and verify NONE are allergens or derivatives!"

    return warning


def _get_json_example(include_recipes: bool, meals_per_day: str) -> str:
    """
    Generate JSON example with the CORRECT meal structure for the user's preference.
    This ensures Claude sees the right pattern to follow.
    """

    # Determine if we should show 5-meal or 3-meal example
    mpd_lower = meals_per_day.lower().strip()
    show_snacks = '2' in mpd_lower and 'snack' in mpd_lower

    if include_recipes:
        if show_snacks:
            # Show 5-meal structure with snacks
            return """[
  {
    "day": "Monday",
    "meals": [
      {
        "type": "breakfast",
        "name": "Greek Yogurt Parfait",
        "calories": 350,
        "description": "...",
        "ingredients": ["1 cup Greek yogurt", "1/2 cup berries"],
        "servings": 1,
        "prep_time_minutes": 5,
        "cook_time_minutes": 0,
        "instructions": ["Layer yogurt and berries"],
        "nutrition": {"protein": "20g", "carbs": "45g", "fat": "8g", "fiber": "6g"}
      },
      {
        "type": "snack",
        "name": "Apple with Almond Butter",
        "calories": 200,
        "description": "...",
        "ingredients": ["1 apple", "2 tbsp almond butter"],
        "servings": 1,
        "prep_time_minutes": 2,
        "cook_time_minutes": 0,
        "instructions": ["Slice apple", "Spread almond butter"],
        "nutrition": {"protein": "5g", "carbs": "25g", "fat": "10g", "fiber": "5g"}
      },
      {
        "type": "lunch",
        "name": "Grilled Chicken Salad",
        "calories": 450,
        "description": "...",
        "ingredients": ["4 oz chicken", "2 cups mixed greens"],
        "servings": 1,
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "instructions": ["Grill chicken", "Toss with greens"],
        "nutrition": {"protein": "35g", "carbs": "20g", "fat": "15g", "fiber": "4g"}
      },
      {
        "type": "snack",
        "name": "Hummus and Veggie Sticks",
        "calories": 150,
        "description": "...",
        "ingredients": ["1/4 cup hummus", "1 cup carrot sticks"],
        "servings": 1,
        "prep_time_minutes": 3,
        "cook_time_minutes": 0,
        "instructions": ["Cut vegetables", "Serve with hummus"],
        "nutrition": {"protein": "6g", "carbs": "18g", "fat": "6g", "fiber": "5g"}
      },
      {
        "type": "dinner",
        "name": "Baked Salmon with Quinoa",
        "calories": 550,
        "description": "...",
        "ingredients": ["5 oz salmon", "1 cup cooked quinoa"],
        "servings": 1,
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
        "instructions": ["Bake salmon at 400°F", "Serve with quinoa"],
        "nutrition": {"protein": "40g", "carbs": "45g", "fat": "18g", "fiber": "6g"}
      }
    ]
  }
]"""
        else:
            # Show 3-meal structure with full recipes
            return """[
  {
    "day": "Monday",
    "meals": [
      {
        "type": "breakfast",
        "name": "Greek Yogurt Parfait with Berries",
        "calories": 350,
        "description": "High-protein breakfast with Greek yogurt, mixed berries, granola, and honey. Rich in probiotics for gut health.",
        "ingredients": [
          "1 cup Greek yogurt (plain, non-fat)",
          "1/2 cup mixed berries (blueberries, strawberries)",
          "1/4 cup granola",
          "1 tbsp honey",
          "1 tbsp chia seeds"
        ],
        "servings": 1,
        "prep_time_minutes": 5,
        "cook_time_minutes": 0,
        "instructions": [
          "Layer half the Greek yogurt in a bowl or glass",
          "Add half the berries on top",
          "Sprinkle with granola and chia seeds",
          "Add remaining yogurt and berries",
          "Drizzle with honey and serve immediately"
        ],
        "nutrition": {
          "protein": "20g",
          "carbs": "45g",
          "fat": "8g",
          "fiber": "6g"
        }
      },
      {
        "type": "lunch",
        "name": "Grilled Salmon Quinoa Bowl",
        "calories": 550,
        "description": "Omega-3 rich salmon with quinoa, spinach, avocado, and lemon dressing.",
        "ingredients": [
          "5 oz salmon fillet",
          "1 cup cooked quinoa",
          "2 cups fresh spinach",
          "1/2 avocado, sliced",
          "1 tbsp olive oil",
          "Lemon juice"
        ],
        "servings": 1,
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
        "instructions": [
          "Season salmon with salt and pepper",
          "Grill salmon for 8-10 minutes per side",
          "Arrange quinoa and spinach in bowl",
          "Top with salmon and avocado",
          "Drizzle with olive oil and lemon juice"
        ],
        "nutrition": {
          "protein": "40g",
          "carbs": "48g",
          "fat": "20g",
          "fiber": "8g"
        }
      },
      {
        "type": "dinner",
        "name": "Herb-Crusted Chicken with Roasted Vegetables",
        "calories": 600,
        "description": "Lean protein with colorful roasted vegetables and sweet potato.",
        "ingredients": [
          "6 oz chicken breast",
          "1 cup broccoli florets",
          "1 bell pepper, sliced",
          "1 medium sweet potato, cubed",
          "2 tbsp olive oil",
          "Mixed herbs (rosemary, thyme)"
        ],
        "servings": 1,
        "prep_time_minutes": 15,
        "cook_time_minutes": 30,
        "instructions": [
          "Preheat oven to 425°F",
          "Coat chicken with herbs",
          "Toss vegetables with olive oil",
          "Arrange on baking sheet",
          "Roast for 25-30 minutes until chicken reaches 165°F"
        ],
        "nutrition": {
          "protein": "45g",
          "carbs": "55g",
          "fat": "18g",
          "fiber": "9g"
        }
      }
    ]
  }
]"""
    else:
        # Non-recipe examples (overview mode)
        if show_snacks:
            # Show 5-meal structure without recipe details
            return """[
  {
    "day": "Monday",
    "meals": [
      {
        "type": "breakfast",
        "name": "Greek Yogurt Parfait with Berries",
        "calories": 350,
        "description": "High-protein breakfast with Greek yogurt, mixed berries, granola, and honey. Rich in probiotics for gut health."
      },
      {
        "type": "snack",
        "name": "Apple with Almond Butter",
        "calories": 200,
        "description": "Sliced apple with natural almond butter. Provides healthy fats and sustained energy."
      },
      {
        "type": "lunch",
        "name": "Grilled Salmon Quinoa Bowl",
        "calories": 550,
        "description": "Omega-3 rich salmon with quinoa, spinach, avocado, and lemon dressing. Supports heart health and energy."
      },
      {
        "type": "snack",
        "name": "Hummus and Veggie Sticks",
        "calories": 150,
        "description": "Hummus with carrot and celery sticks. Light, nutritious afternoon snack."
      },
      {
        "type": "dinner",
        "name": "Herb-Crusted Chicken with Roasted Vegetables",
        "calories": 600,
        "description": "Lean protein with colorful roasted vegetables (broccoli, bell peppers, carrots) and sweet potato."
      }
    ]
  },
  {
    "day": "Tuesday",
    "meals": [...]
  }
]"""
        else:
            # Show 3-meal structure without recipe details
            return """[
  {
    "day": "Monday",
    "meals": [
      {
        "type": "breakfast",
        "name": "Greek Yogurt Parfait with Berries",
        "calories": 350,
        "description": "High-protein breakfast with Greek yogurt, mixed berries, granola, and honey. Rich in probiotics for gut health."
      },
      {
        "type": "lunch",
        "name": "Grilled Salmon Quinoa Bowl",
        "calories": 550,
        "description": "Omega-3 rich salmon with quinoa, spinach, avocado, and lemon dressing. Supports heart health and energy."
      },
      {
        "type": "dinner",
        "name": "Herb-Crusted Chicken with Roasted Vegetables",
        "calories": 600,
        "description": "Lean protein with colorful roasted vegetables (broccoli, bell peppers, carrots) and sweet potato."
      }
    ]
  },
  {
    "day": "Tuesday",
    "meals": [...]
  }
]"""


async def generate_llm_meal_plan(user: User, num_days: int, include_recipes: bool = False) -> List[DailyMealPlan]:
    """
    Generate a personalized meal plan using Claude Haiku LLM.

    This function:
    1. Retrieves user survey data from preferences
    2. Constructs a detailed prompt for Claude Haiku with optional recipe details
    3. Calls the Anthropic API asynchronously
    4. Parses and validates the JSON response
    5. Returns validated Pydantic models

    Args:
        user: User object with preferences containing survey_data
        num_days: Number of days for the meal plan (1-14)
        include_recipes: If True, generate detailed recipes with ingredients and instructions

    Returns:
        List[DailyMealPlan]: Validated meal plan data

    Raises:
        HTTPException: If user survey data is missing
        LLMResponseError: If LLM response cannot be parsed or validated
    """

    # Validate user has survey data
    if not user.preferences:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User preferences not found. Please complete the survey first."
        )

    survey_data = user.preferences.get("survey_data")
    if not survey_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User survey data not found. Please complete the onboarding survey."
        )

    # Validate API key is configured
    if not settings.anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY not configured")
        raise LLMResponseError("LLM service is not configured. Please contact support.")

    # Initialize Anthropic async client
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    try:
        # Generate the prompt
        prompt = generate_meal_plan_prompt(survey_data, num_days, include_recipes)

        # Choose model based on environment variable or default to Sonnet
        model_name = "claude-3-5-sonnet-20241022"  # Testing Sonnet
        max_tokens = 8192  # Sonnet supports more tokens
        logger.info(f"Generating meal plan for user {user.id} with Claude 3.5 Sonnet (recipes={include_recipes})")

        # Call Claude API
        message = await client.messages.create(
            model=model_name,
            max_tokens=max_tokens,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract text response
        llm_response_text = message.content[0].text

        logger.debug(f"Raw LLM response: {llm_response_text[:500]}...")

        # Parse JSON response
        try:
            parsed_json = json.loads(llm_response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Invalid JSON response: {llm_response_text[:1000]}")
            raise LLMResponseError(f"Failed to parse LLM response as JSON: {str(e)}")

        # Validate with Pydantic
        try:
            # Parse list of DailyMealPlan objects
            validated_plan = [DailyMealPlan.model_validate(day) for day in parsed_json]
        except ValidationError as e:
            logger.error(f"Pydantic validation error: {e}")
            logger.error(f"Invalid data structure: {parsed_json}")
            raise LLMResponseError(f"Failed to validate LLM response structure: {str(e)}")

        # If overview mode, strip out optional recipe fields that Claude helpfully added
        if not include_recipes:
            for day in validated_plan:
                for meal in day.meals:
                    # Set all optional recipe fields to None
                    meal.ingredients = None
                    meal.servings = None
                    meal.prep_time_minutes = None
                    meal.cook_time_minutes = None
                    meal.instructions = None
                    meal.nutrition = None

        logger.info(f"Successfully generated {len(validated_plan)} day meal plan for user {user.id}")

        return validated_plan

    except LLMResponseError:
        # Re-raise our custom errors
        raise
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected error in LLM meal plan generation: {str(e)}")
        raise LLMResponseError(f"Unexpected error generating meal plan: {str(e)}")
