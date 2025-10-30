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
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

/**
 * Update user's daily calorie goal
 * @param {number} goalCalories - Daily calorie goal
 * @returns {Promise<Object>} Response with goal data
 */
export const updateDailyCalorieGoal = async (goalCalories) => {
  const response = await fetch(`${API_BASE_URL}${API_PREFIX}/calorie/goal`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({ goal_calories: goalCalories }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to update calorie goal');
  }
  return response.json();
};

/**
 * Log calorie intake
 * @param {string} mealType - Type of meal (Breakfast, Lunch, Dinner, Snack)
 * @param {number} caloriesConsumed - Calories consumed
 * @returns {Promise<Object>} Response with entry and updated summary
 */
export const logCalorieIntake = async (mealType, caloriesConsumed) => {
  const response = await fetch(`${API_BASE_URL}${API_PREFIX}/calorie/intake`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      meal_type: mealType,
      calories_consumed: caloriesConsumed,
    }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to log calorie intake');
  }
  return response.json();
};

/**
 * Get daily calorie summary
 * @param {string} targetDate - Optional date in YYYY-MM-DD format (defaults to today)
 * @returns {Promise<Object>} Summary data transformed for frontend
 */
export const getDailyCalorieSummary = async (targetDate = null) => {
  const url = targetDate
    ? `${API_BASE_URL}${API_PREFIX}/calorie/summary?target_date=${targetDate}`
    : `${API_BASE_URL}${API_PREFIX}/calorie/summary`;
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to get calorie summary');
  }
  return response.json();
};
