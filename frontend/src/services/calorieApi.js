/**
 * API service for calorie tracking
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const API_PREFIX = '/api/v1';

/**
 * Get authentication token from localStorage
 */
const getAuthToken = () => {
  return localStorage.getItem('token');
};

/**
 * Get authentication headers
 */
const getAuthHeaders = () => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

/**
 * Update user's daily calorie goal
 * @param {number} goalCalories - Daily calorie goal
 * @returns {Promise<Object>} Response with goal data
 */
export const updateDailyCalorieGoal = async (goalCalories) => {
  try {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/calorie/goal`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify({ goal_calories: goalCalories })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update calorie goal');
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating calorie goal:', error);
    throw error;
  }
};

/**
 * Log calorie intake
 * @param {string} mealType - Type of meal (Breakfast, Lunch, Dinner, Snack)
 * @param {number} caloriesConsumed - Calories consumed
 * @returns {Promise<Object>} Response with entry and updated summary
 */
export const logCalorieIntake = async (mealType, caloriesConsumed) => {
  try {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/calorie/intake`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        meal_type: mealType,
        calories_consumed: caloriesConsumed
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to log calorie intake');
    }

    return await response.json();
  } catch (error) {
    console.error('Error logging calorie intake:', error);
    throw error;
  }
};

/**
 * Get daily calorie summary
 * @param {string} targetDate - Optional date in YYYY-MM-DD format (defaults to today)
 * @returns {Promise<Object>} Summary data transformed for frontend
 */
export const getDailyCalorieSummary = async (targetDate = null) => {
  try {
    const url = targetDate
      ? `${API_BASE_URL}${API_PREFIX}/calorie/summary?target_date=${targetDate}`
      : `${API_BASE_URL}${API_PREFIX}/calorie/summary`;

    const response = await fetch(url, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get calorie summary');
    }

    const data = await response.json();

    // Transform backend response to match frontend expectations
    return {
      goal_calories: data.goal_calories,
      total_intake: data.total_intake,
      remaining_calories: data.remaining_calories,
      percentage: data.percentage,
      entries: data.entries || [],
      entry_date: data.entry_date,
      // For Dashboard compatibility
      calories: {
        current: data.total_intake,
        target: data.goal_calories || 2000, // Default to 2000 if no goal set
        percentage: Math.round(data.percentage)
      }
    };
  } catch (error) {
    console.error('Error getting calorie summary:', error);
    throw error;
  }
};
