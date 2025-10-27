/**
 * API service for AI-powered meal plan generation and survey submission
 *
 * This service handles all communication with the backend for:
 * - Submitting user survey data (dietary preferences, health goals, allergies, etc.)
 * - Generating personalized meal plans using Claude Haiku LLM
 * - Managing authentication tokens for secure API requests
 */

// ============================================================================
// Configuration
// ============================================================================

/**
 * Base API URL from environment variable or default to local development server
 * Uses Vite's import.meta.env for environment variables
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Get authentication token from localStorage
 *
 * Note: This uses 'token' key (not 'auth_token') to match AuthContext implementation.
 * AuthContext stores the token as localStorage.setItem('token', newToken)
 *
 * @returns {string|null} JWT token or null if not authenticated
 */
const getAuthToken = () => {
  return localStorage.getItem('token');
};

/**
 * Get authentication headers for API requests
 *
 * Returns headers object with:
 * - Content-Type for JSON requests
 * - Authorization Bearer token if user is authenticated
 *
 * @returns {Object} Headers object for fetch requests
 */
const getAuthHeaders = () => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

// ============================================================================
// API Functions
// ============================================================================

/**
 * Submit user survey data from onboarding flow
 *
 * This endpoint processes the user's health goals, dietary restrictions, allergies,
 * and meal preferences. The backend translates health pillar names to IDs and stores
 * both the survey data and translated goals in user preferences.
 *
 * @param {Object} surveyData - Complete survey data from NutriTest
 * @param {string[]} surveyData.healthPillars - Selected health pillar names (e.g., ["Increased Energy", "Heart Health"])
 * @param {string[]} surveyData.dietaryRestrictions - Dietary restrictions (e.g., ["vegetarian", "gluten-free"])
 * @param {string} surveyData.mealComplexity - Preferred meal complexity ("simple", "moderate", "complex")
 * @param {string[]} surveyData.dislikedIngredients - Ingredients to avoid (e.g., ["mushrooms", "olives"])
 * @param {string} surveyData.mealsPerDay - Meal structure ("3", "3-meals-2-snacks", "6")
 * @param {string[]} surveyData.allergies - Food allergies (e.g., ["peanuts", "shellfish"])
 * @param {string} surveyData.primaryGoal - Primary health/wellness goal
 *
 * @returns {Promise<Object>} Updated user profile with survey data stored in preferences
 *
 * @throws {Error} If survey submission fails or validation errors occur
 *
 * @example
 * const surveyData = {
 *   healthPillars: ["Increased Energy", "Weight Management"],
 *   dietaryRestrictions: ["vegetarian"],
 *   mealComplexity: "moderate",
 *   dislikedIngredients: ["mushrooms"],
 *   mealsPerDay: "3-meals-2-snacks",
 *   allergies: ["peanuts"],
 *   primaryGoal: "Lose weight and increase energy"
 * };
 * const response = await submitSurvey(surveyData);
 */
export const submitSurvey = async (surveyData) => {
  try {
    // First, fetch health pillars to convert IDs to names
    let healthPillarNames = [];
    if (surveyData.healthPillars && surveyData.healthPillars.length > 0) {
      try {
        // Fetch all health pillars
        const pillarsResponse = await fetch(`${API_BASE_URL}/health/pillars`, {
          headers: getAuthHeaders()
        });

        if (pillarsResponse.ok) {
          const pillars = await pillarsResponse.json();
          console.log('📋 Fetched pillars from API:', pillars);
          console.log('🎯 Survey health pillar IDs:', surveyData.healthPillars);

          // Map selected IDs to names
          healthPillarNames = surveyData.healthPillars
            .map(id => {
              const pillar = pillars.find(p => p.id === id);
              console.log(`  Mapping ID ${id} to:`, pillar ? pillar.name : 'NOT FOUND');
              return pillar ? pillar.name : null;
            })
            .filter(name => name !== null);  // Remove nulls

          console.log('✅ Final health pillar names:', healthPillarNames);
        }
      } catch (err) {
        console.error('❌ CRITICAL: Error fetching health pillars:', err);
        // Don't use a fallback - throw error so user knows there's a problem
        throw new Error(`Failed to load health pillar data. Please refresh the page and try again. Error: ${err.message}`);
      }
    }

    // Transform frontend data structure to match backend schema
    const transformedData = {
      healthPillars: healthPillarNames,
      dietaryRestrictions: surveyData.diets || [],  // Map 'diets' to 'dietaryRestrictions'
      mealComplexity: surveyData.mealComplexity || 'moderate',  // Default to 'moderate'
      dislikedIngredients: surveyData.dislikedIngredients || [],
      mealsPerDay: surveyData.mealsPerDay || '3',  // Default to '3' (matches backend mapping)
      allergies: surveyData.allergies || [],
      primaryGoal: healthPillarNames[0] || 'General wellness'  // Use first pillar name as primaryGoal
    };

    const response = await fetch(`${API_BASE_URL}/users/me/survey`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(transformedData)
    });

    // Handle non-200 responses
    if (!response.ok) {
      const errorData = await response.json();

      // Handle validation errors (422)
      if (response.status === 422 && errorData.detail) {
        // Format Pydantic validation errors for display
        if (Array.isArray(errorData.detail)) {
          const errors = errorData.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
          throw new Error(`Validation error: ${errors}`);
        }
      }

      const errorMessage = errorData?.detail || 'Failed to submit survey';
      throw new Error(errorMessage);
    }

    // Return the updated user profile
    return await response.json();
  } catch (error) {
    // Re-throw with context if it's a network error
    if (error.message === 'Failed to fetch') {
      throw new Error('Network error: Unable to connect to backend. Please check your connection.');
    }
    throw error;
  }
};

/**
 * Generate AI-powered personalized meal plan
 *
 * Uses Claude Haiku LLM to generate a 1-day meal plan based on the user's
 * survey data (stored in backend preferences). The plan respects all dietary
 * restrictions, allergies, and addresses selected health goals.
 *
 * @param {boolean} includeRecipes - Whether to include full recipe details (ingredients, instructions, etc.)
 *   - false: Returns basic meal info (name, calories, description)
 *   - true: Returns complete recipes with ingredients, servings, prep time, cook time, instructions, and nutrition
 *
 * @returns {Promise<Object>} Meal plan response object
 * @returns {Object[]} return.plan - Array of daily meal plans (currently 1 day)
 * @returns {string} return.plan[].day - Day label (e.g., "Day 1")
 * @returns {Object[]} return.plan[].meals - Array of meals for the day
 * @returns {string} return.plan[].meals[].type - Meal type ("breakfast", "lunch", "dinner", "snack")
 * @returns {string} return.plan[].meals[].name - Meal name
 * @returns {number} return.plan[].meals[].calories - Estimated calories
 * @returns {string} return.plan[].meals[].description - Meal description
 * @returns {string[]?} return.plan[].meals[].ingredients - Optional: List of ingredients with measurements
 * @returns {number?} return.plan[].meals[].servings - Optional: Number of servings
 * @returns {number?} return.plan[].meals[].prep_time_minutes - Optional: Prep time in minutes
 * @returns {number?} return.plan[].meals[].cook_time_minutes - Optional: Cook time in minutes
 * @returns {string[]?} return.plan[].meals[].instructions - Optional: Step-by-step cooking instructions
 * @returns {Object?} return.plan[].meals[].nutrition - Optional: Detailed nutrition info (protein, carbs, fat, fiber)
 * @returns {string?} return.health_goal_summary - Summary of how the plan addresses user's health goals
 *
 * @throws {Error} If meal plan generation fails (503 service unavailable)
 * @throws {Error} If user has no survey data (400 bad request)
 *
 * @example
 * // Generate basic meal plan
 * const basicPlan = await generateMealPlan(false);
 * console.log(basicPlan.plan[0].meals); // Array of 5 meals with basic info
 *
 * @example
 * // Generate detailed meal plan with recipes
 * const detailedPlan = await generateMealPlan(true);
 * const firstMeal = detailedPlan.plan[0].meals[0];
 * console.log(firstMeal.ingredients); // ["2 cups oats", "1 banana", ...]
 * console.log(firstMeal.instructions); // ["Step 1...", "Step 2...", ...]
 */
export const generateMealPlan = async (includeRecipes = false) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/users/me/llm-meal-plan?include_recipes=${includeRecipes}`,
      {
        method: 'POST',
        headers: getAuthHeaders()
      }
    );

    // Handle non-200 responses
    if (!response.ok) {
      const errorData = await response.json();
      const errorMessage = errorData?.detail || 'Failed to generate meal plan';

      // Provide user-friendly error messages based on status code
      if (response.status === 503) {
        throw new Error('Meal plan service temporarily unavailable. Please try again in a moment.');
      } else if (response.status === 400) {
        throw new Error('Please complete the NutriTest survey before generating a meal plan.');
      }

      throw new Error(errorMessage);
    }

    // Return the meal plan response
    return await response.json();
  } catch (error) {
    // Re-throw with context if it's a network error
    if (error.message === 'Failed to fetch') {
      throw new Error('Network error: Unable to connect to backend. Please check your connection.');
    }
    throw error;
  }
};

// ============================================================================
// Export all functions
// ============================================================================

export default {
  submitSurvey,
  generateMealPlan
};
