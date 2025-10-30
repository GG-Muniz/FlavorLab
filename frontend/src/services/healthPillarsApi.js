/**
 * API service for health pillars
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const buildUrl = (path) => {
  const normalizedBase = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
};

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
 * Fetch all available health pillars
 * @returns {Promise<Array>} Array of health pillar objects
 */
export const getHealthPillars = async () => {
  const response = await fetch(buildUrl('health/pillars'), {
    method: 'GET',
    headers: getAuthHeaders()
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch health pillars');
  }
  return await response.json();
};

/**
 * Save user's selected health pillars
 * @param {Array<number>} pillarIds - Array of selected pillar IDs
 * @returns {Promise<Object>} Response with saved preferences
 */
export const saveUserHealthPillars = async (pillarIds) => {
  const response = await fetch(buildUrl('users/preferences'), {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ health_pillar_ids: pillarIds })
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to save health pillar preferences');
  }
  return await response.json();
};

/**
 * Get user's selected health pillars
 * @returns {Promise<Object>} User preferences with selected pillars
 */
export const getUserHealthPillars = async () => {
  const response = await fetch(buildUrl('users/preferences'), {
    method: 'GET',
    headers: getAuthHeaders()
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch user health pillar preferences');
  }
  return await response.json();
};
