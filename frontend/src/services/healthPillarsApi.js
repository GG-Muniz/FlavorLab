/**
 * API service for health pillars
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

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
 * Fetch all available health pillars
 * @returns {Promise<Array>} Array of health pillar objects
 */
export const getHealthPillars = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health/pillars`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch health pillars');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching health pillars:', error);
    throw error;
  }
};

/**
 * Save user's selected health pillars
 * @param {Array<number>} pillarIds - Array of selected pillar IDs
 * @returns {Promise<Object>} Response with saved preferences
 */
export const saveUserHealthPillars = async (pillarIds) => {
  try {
    // Backend expects HealthGoalsUpdate { selectedGoals: number[] } at /users/me/health-goals
    const response = await fetch(`${API_BASE_URL}/users/me/health-goals`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ selectedGoals: pillarIds })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to save health pillar preferences');
    }

    return await response.json();
  } catch (error) {
    console.error('Error saving health pillar preferences:', error);
    throw error;
  }
};

/**
 * Get user's selected health pillars
 * @returns {Promise<Object>} User preferences with selected pillars
 */
export const getUserHealthPillars = async () => {
  try {
    // Fetch profile and derive goals from preferences or top-level
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch user health pillar preferences');
    }

    const profile = await response.json();
    const prefs = profile?.preferences || {};
    const top = profile?.health_goals;
    const selected = Array.isArray(prefs.health_goals)
      ? prefs.health_goals
      : (Array.isArray(top?.selectedGoals) ? top.selectedGoals : (Array.isArray(top) ? top : []));
    return { selectedGoals: selected };
  } catch (error) {
    console.error('Error fetching user health pillar preferences:', error);
    throw error;
  }
};
