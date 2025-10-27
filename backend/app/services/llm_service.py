"""
LLM service for generating personalized meal plans using Claude Haiku or ChatGPT.

This module provides functionality to interact with Anthropic Claude API and OpenAI API
to generate AI-powered meal plans based on user survey data and preferences.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
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


# Initialize the async clients
settings = get_settings()
anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


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

    # Debug logging
    logger.info(f"🎯 Health Pillars for LLM prompt: {health_pillars}")
    logger.info(f"📊 Survey data keys: {list(survey_data.keys())}")

    # Format critical constraints (allergies, dietary restrictions, disliked ingredients)
    critical_constraints = ""
    constraint_sections = []

    # Allergy constraints - highest priority
    if allergies:
        allergy_list = ", ".join(allergies)
        constraint_sections.append(f"""
🚨 ALLERGY SAFETY CONSTRAINT 🚨
The user has LIFE-THREATENING allergies to: {allergy_list}
ABSOLUTELY FORBIDDEN: Never include these ingredients or any derivatives.
- Check EVERY ingredient, seasoning, and garnish
- Avoid related terms (e.g., "dairy" means no milk, cheese, butter, cream, yogurt, whey, casein)
- When in doubt, exclude the ingredient
This is a MEDICAL SAFETY requirement - violations could harm the user.
""")

    # Dietary restrictions - must be strictly followed
    if dietary_restrictions:
        restriction_details = {
            "vegan": "NO animal products (meat, poultry, fish, seafood, eggs, dairy, honey)",
            "vegetarian": "NO meat, poultry, fish, or seafood (eggs and dairy are OK)",
            "gluten-free": "NO wheat, barley, rye, malt, or derivatives (bread, pasta, flour, beer, soy sauce)",
            "dairy-free": "NO milk, cheese, butter, cream, yogurt, whey, casein, or derivatives",
            "keto": "HIGH fat, MODERATE protein, VERY LOW carbs (<20g net carbs per day)",
            "paleo": "NO grains, legumes, dairy, refined sugar, or processed foods"
        }
        restriction_list = [restriction_details.get(r, r) for r in dietary_restrictions]
        constraint_sections.append(f"""
DIETARY RESTRICTION MANDATE:
{chr(10).join(f"- {r}" for r in restriction_list)}
Verify that EVERY meal and ingredient complies with these restrictions.
""")

    # Disliked ingredients - must be avoided
    if disliked_ingredients:
        disliked_list = ", ".join(disliked_ingredients)
        constraint_sections.append(f"""
DISLIKED INGREDIENTS TO AVOID:
The user dislikes: {disliked_list}
Do NOT include these ingredients or feature them prominently in any meal.
""")

    if constraint_sections:
        critical_constraints = "\n" + "\n".join(constraint_sections)

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

    # Build an example JSON structure to avoid brace-escaping issues in f-strings
    example_meal = {
        "type": "breakfast",
        "name": "Meal Name",
        "calories": 400,
        "description": "Brief description",
        "tags": ["Gluten-Free", "High-Protein", "Quick-Meal"]
    }
    if include_recipes:
        example_meal.update({
            "ingredients": ["ingredient 1", "ingredient 2"],
            "servings": 2,
            "prep_time_minutes": 10,
            "cook_time_minutes": 15,
            "instructions": ["step 1", "step 2"],
            "nutrition": {"protein": "20g", "carbs": "45g", "fat": "12g"},
        })
    example_day = {"day": "Day 1", "meals": [example_meal]}
    example_json = json.dumps([example_day], indent=2)

    # Build the complete prompt with constraints at the top
    prompt = f"""You are FlavorLab's expert nutritionist and meal planning AI. Create a personalized {num_days}-day meal plan.
{critical_constraints}
## CONSTRAINT VERIFICATION CHECKLIST
Before finalizing each meal, verify:
✓ Contains NO allergens or their derivatives
✓ Complies with ALL dietary restrictions (check each ingredient)
✓ Excludes ALL disliked ingredients
✓ Uses appropriate ingredient names (e.g., "coconut cream" not "cream", "almond butter" not "butter")

## CONSTRAINT CONFIRMATION TAGGING MANDATE
For each meal you generate, you MUST populate the 'tags' array with labels that explicitly confirm you have respected the user's survey data. This is the most critical step for building user trust. Follow these rules precisely:

1. **Dietary Restrictions (MANDATORY):** For EVERY dietary restriction the user has (e.g., 'gluten-free', 'vegetarian', 'keto'), you MUST add a corresponding tag (e.g., "Gluten-Free", "Vegetarian", "Keto"). This confirms compliance.

2. **Allergies (MANDATORY):** For EVERY allergy the user has (e.g., 'dairy', 'peanuts', 'shellfish'), you MUST add a corresponding "X-Free" tag (e.g., "Dairy-Free", "Peanut-Free", "Shellfish-Free"). This confirms safety. Include ALL allergy tags even if they seem obvious (e.g., "Shellfish-Free" for vegetarian meals).

3. **Health Goal Tagging (CRITICAL):** For each meal, you MUST analyze its ingredients and nutritional benefits. If the meal directly supports one or more of the user's selected Health Goals (ONLY: {', '.join(health_pillars)}), you MUST add a tag for EACH supported goal. The tag MUST be the EXACT name of the Health Goal from the user profile (character-for-character match). This is the primary way the user will see the value of their personalized plan. Every meal should support at least one health goal. FORBIDDEN: Do NOT use "General Wellness" or any generic health terms - ONLY use the exact pillar names listed above.

4. **Disliked Ingredients (OPTIONAL):** If the user dislikes an ingredient (e.g., 'cilantro'), and the meal avoids it, you MAY add a "No [Ingredient]" tag, but this is less critical.

5. **STRICTLY FORBIDDEN - No Generic Tags:** Do NOT add ANY generic nutritional tags like "High-Protein", "High-Fiber", "Low-Carb", "Quick-Meal", "Heart-Healthy", "General Wellness", "Balanced", etc. These do not confirm user constraints and undermine trust. The ONLY acceptable tags are those that directly mirror the user's stated dietary restrictions, allergies, and health pillar names from the lists above.

**Example:** If the user is 'gluten-free', 'vegetarian', has a 'dairy' allergy, and selected 'Improved Digestion' as a health pillar, a valid meal's tags would be ["Gluten-Free", "Vegetarian", "Dairy-Free", "Improved Digestion"].

## DAILY MEAL STRUCTURE MANDATE
Each day MUST have exactly this structure: {meal_structure}

## USER PROFILE
🎯 **EXACT Health Goal Names to Use in Tags (copy these exactly):**
{chr(10).join(f'   - "{pillar}"' for pillar in health_pillars) if health_pillars else '   - None'}

- Primary Goal: {primary_goal}
- Dietary Restrictions: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}
- Meal Complexity: {meal_complexity}
- Disliked Ingredients: {', '.join(disliked_ingredients) if disliked_ingredients else 'None'}
{preferred_ingredients_section}
## REQUIREMENTS
1. Address all health goals through food choices
2. Respect all dietary restrictions strictly (see detailed restrictions above)
3. Avoid all disliked ingredients completely
4. Match the specified meal complexity level
5. Each day must follow the meal structure: {meal_structure}
6. Use specific ingredient names to avoid ambiguity (e.g., "plant-based milk" instead of "milk")
{recipe_section}

## JSON-ONLY MANDATE
Respond ONLY with a JSON array. No markdown, no explanations, no code blocks.
The JSON must be a valid array matching this structure (example only):

{example_json}

Generate the {num_days}-day meal plan now as pure JSON:"""

    return prompt


async def generate_llm_meal_plan_anthropic(
    survey_data: dict,
    num_days: int,
    include_recipes: bool,
    preferred_ingredient_names: Optional[List[str]],
    user_id: int,
    model: str = "claude-3-5-haiku-20241022"
) -> List[DailyMealPlan]:
    """
    Generate meal plan using Anthropic Claude API.

    Args:
        survey_data: User's survey data
        num_days: Number of days for the meal plan
        include_recipes: Whether to include detailed recipe information
        preferred_ingredient_names: List of preferred ingredient names
        user_id: User ID for logging
        model: Claude model to use

    Returns:
        List[DailyMealPlan]: Validated list of daily meal plans
    """
    prompt = generate_meal_plan_prompt(
        survey_data,
        num_days,
        include_recipes,
        preferred_ingredients=preferred_ingredient_names if preferred_ingredient_names else None
    )

    logger.info(f"Generating meal plan with Anthropic Claude ({model}) for user {user_id}")

    message = await anthropic_client.messages.create(
        model=model,
        max_tokens=8000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    response_text = message.content[0].text.strip()
    logger.debug(f"Claude response: {response_text[:500]}...")

    try:
        meal_plan_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response as JSON: {e}")
        logger.error(f"Response text: {response_text}")
        raise LLMResponseError(f"Claude returned invalid JSON: {e}")

    validated_plans = [DailyMealPlan.model_validate(day) for day in meal_plan_data]
    logger.info(f"Successfully generated and validated {len(validated_plans)} days with Claude")
    return validated_plans


async def generate_llm_meal_plan_openai(
    survey_data: dict,
    num_days: int,
    include_recipes: bool,
    preferred_ingredient_names: Optional[List[str]],
    user_id: int,
    model: str = "gpt-4o-mini"
) -> List[DailyMealPlan]:
    """
    Generate meal plan using OpenAI ChatGPT API.

    Args:
        survey_data: User's survey data
        num_days: Number of days for the meal plan
        include_recipes: Whether to include detailed recipe information
        preferred_ingredient_names: List of preferred ingredient names
        user_id: User ID for logging
        model: OpenAI model to use (gpt-4o-mini or gpt-4o)

    Returns:
        List[DailyMealPlan]: Validated list of daily meal plans
    """
    if not openai_client:
        raise LLMResponseError("OpenAI client not initialized. Check OPENAI_API_KEY in .env")

    prompt = generate_meal_plan_prompt(
        survey_data,
        num_days,
        include_recipes,
        preferred_ingredients=preferred_ingredient_names if preferred_ingredient_names else None
    )

    logger.info(f"Generating meal plan with OpenAI ({model}) for user {user_id}")

    response = await openai_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are FlavorLab's expert nutritionist. Respond with valid JSON only, no markdown or code blocks."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=8000,
        temperature=0.7
    )

    response_text = response.choices[0].message.content.strip()
    logger.debug(f"OpenAI response: {response_text[:500]}...")

    try:
        # OpenAI might wrap in a root object, handle both cases
        parsed_json = json.loads(response_text)

        # If it's a single day object with "day" and "meals" keys, wrap it in an array
        if isinstance(parsed_json, dict) and "day" in parsed_json and "meals" in parsed_json:
            meal_plan_data = [parsed_json]
        # If wrapped in a root key, try to extract the array
        elif isinstance(parsed_json, dict) and len(parsed_json) == 1:
            value = list(parsed_json.values())[0]
            # Check if the value is already an array or needs wrapping
            if isinstance(value, list):
                meal_plan_data = value
            elif isinstance(value, dict) and "day" in value:
                meal_plan_data = [value]
            else:
                meal_plan_data = value
        else:
            meal_plan_data = parsed_json

        # Ensure it's a list
        if not isinstance(meal_plan_data, list):
            raise ValueError("Response is not a list of daily meal plans")

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {e}")
        logger.error(f"Response text: {response_text}")
        raise LLMResponseError(f"OpenAI returned invalid JSON: {e}")

    validated_plans = [DailyMealPlan.model_validate(day) for day in meal_plan_data]
    logger.info(f"Successfully generated and validated {len(validated_plans)} days with OpenAI")
    return validated_plans


async def generate_llm_meal_plan(
    user: User,
    num_days: int = 1,
    include_recipes: bool = False,
    db: Session = None,
    provider: Optional[str] = None,
    model: Optional[str] = None
) -> List[DailyMealPlan]:
    """
    Generate a personalized meal plan using Claude Haiku or ChatGPT.

    Args:
        user: User model with preferences containing survey_data
        num_days: Number of days for the meal plan (default: 1)
        include_recipes: Whether to include detailed recipe information (default: False)
        db: Database session for fetching preferred ingredients (optional)
        provider: LLM provider to use ("anthropic" or "openai", defaults to config)
        model: Specific model to use (defaults to config or provider default)

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

        # Determine provider and model
        selected_provider = provider or settings.llm_provider
        selected_model = model or settings.llm_model

        # Route to appropriate provider
        if selected_provider == "openai":
            return await generate_llm_meal_plan_openai(
                survey_data=survey_data,
                num_days=num_days,
                include_recipes=include_recipes,
                preferred_ingredient_names=preferred_ingredient_names,
                user_id=user.id,
                model=selected_model if selected_model.startswith("gpt-") else "gpt-4o-mini"
            )
        else:  # Default to Anthropic
            return await generate_llm_meal_plan_anthropic(
                survey_data=survey_data,
                num_days=num_days,
                include_recipes=include_recipes,
                preferred_ingredient_names=preferred_ingredient_names,
                user_id=user.id,
                model=selected_model if selected_model.startswith("claude-") else "claude-3-5-haiku-20241022"
            )

    except (ValueError, LLMResponseError):
        # Re-raise expected errors
        raise
    except ValidationError as e:
        logger.error(f"Failed to validate LLM response against schema: {e}")
        raise LLMResponseError(f"LLM response does not match expected schema: {e}")
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error generating LLM meal plan: {e}")
        raise LLMResponseError(f"Failed to generate meal plan: {e}")
