/**
 * API service for AI-powered meal plan generation and survey submission
 *
 * This service handles all communication with the backend for:
 * - Submitting user survey data (dietary preferences, health goals, allergies, etc.)
 * - Generating personalized meal plans using Claude Haiku LLM
 * - Managing authentication tokens for secure API requests
 */

// Utilities for survey submission and LLM meal plan generation.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const getAuthToken = () => {
  return localStorage.getItem('token');
};

const getAuthHeaders = () => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
};

export const submitSurvey = async (surveyData) => {
  try {
    let healthPillarNames = [];
    if (surveyData.healthPillars && surveyData.healthPillars.length > 0) {
      try {
        const pillarsResponse = await fetch(`${API_BASE_URL}/health/pillars`, {
          headers: getAuthHeaders()
        });

        if (pillarsResponse.ok) {
          const pillars = await pillarsResponse.json();
          healthPillarNames = surveyData.healthPillars
            .map(id => {
              const pillar = pillars.find(p => p.id === id);
              return pillar ? pillar.name : null;
            })
            .filter(Boolean);
        }
      } catch (err) {
        console.error('Error fetching health pillars:', err);
        healthPillarNames = surveyData.healthPillars.map(id => `Goal ${id}`);
      }
    }

    const transformedData = {
      healthPillars: healthPillarNames,
      dietaryRestrictions: surveyData.diets || [],
      mealComplexity: surveyData.mealComplexity || 'moderate',
      dislikedIngredients: surveyData.dislikedIngredients || [],
      mealsPerDay: surveyData.mealsPerDay || '3',
      allergies: surveyData.allergies || [],
      primaryGoal: healthPillarNames[0] || 'General wellness'
    };

    const response = await fetch(`${API_BASE_URL}/users/me/survey`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(transformedData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      if (response.status === 422 && errorData.detail && Array.isArray(errorData.detail)) {
        const errors = errorData.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
        throw new Error(`Validation error: ${errors}`);
      }
      throw new Error(errorData?.detail || 'Failed to submit survey');
    }

    return await response.json();
  } catch (error) {
    if (error.message === 'Failed to fetch') {
      throw new Error('Network error: Unable to connect to backend. Please check your connection.');
    }
    throw error;
  }
};

export const generateMealPlan = async (includeRecipes = false) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/users/me/llm-meal-plan?include_recipes=${includeRecipes}`,
      {
        method: 'POST',
        headers: getAuthHeaders()
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      if (response.status === 503) {
        throw new Error('Meal plan service temporarily unavailable. Please try again in a moment.');
      } else if (response.status === 400) {
        throw new Error('Please complete the NutriTest survey before generating a meal plan.');
      }
      throw new Error(errorData?.detail || 'Failed to generate meal plan');
    }

    return await response.json();
  } catch (error) {
    if (error.message === 'Failed to fetch') {
      throw new Error('Network error: Unable to connect to backend. Please check your connection.');
    }
    throw error;
  }
};

export default {
  submitSurvey,
  generateMealPlan
};
