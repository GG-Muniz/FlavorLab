/**
 * API service for health pillars
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const API_PREFIX = '/api/v1';

/**
 * Get authentication token from localStorage
 */
const getAuthToken = () => {
  return localStorage.getItem('auth_token');
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
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/health/pillars`, {
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
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/users/preferences`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        health_pillar_ids: pillarIds
      })
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
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/users/preferences`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch user health pillar preferences');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching user health pillar preferences:', error);
    throw error;
  }
};
