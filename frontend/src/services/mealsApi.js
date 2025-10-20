// mealsApi.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

function authHeaders() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
}

async function safeJson(res) {
  const text = await res.text();
  try { return text ? JSON.parse(text) : {}; } catch { return {}; }
}

export async function searchIngredients(query, limit = 10, offset = 0) {
  const res = await fetch(`${API_BASE_URL}/entities/search`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ query, primary_classification: 'ingredient', limit, offset })
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Search failed');
  return Array.isArray(data?.entities) ? data.entities : [];
}

export async function logMeal({ log_date, meal_type, entries }) {
  const res = await fetch(`${API_BASE_URL}/meals/log`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ log_date, meal_type, entries })
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to log meal');
  return data;
}

/**
 * Get all meals for the current user, optionally filtered by source.
 * @param {string} source - Filter by source: 'generated' or 'logged' (optional)
 * @returns {Promise<Array>} Array of meal objects
 */
export async function getMeals(source = null) {
  const url = source
    ? `${API_BASE_URL}/meals?source=${source}`
    : `${API_BASE_URL}/meals`;

  const res = await fetch(url, {
    method: 'GET',
    headers: authHeaders(),
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to fetch meals');
  return Array.isArray(data) ? data : [];
}

/**
 * Log a meal template as a consumed meal.
 * @param {number} templateId - ID of the meal template to log
 * @param {string} logDate - Date to log the meal (YYYY-MM-DD)
 * @returns {Promise<Object>} The logged meal object
 */
export async function logMealFromTemplate(templateId, logDate) {
  const res = await fetch(`${API_BASE_URL}/meals/log-from-template/${templateId}`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ log_date: logDate })
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to log meal from template');
  return data;
}

/**
 * Get calendar integration links for a meal.
 * @param {number} mealId - ID of the meal
 * @returns {Promise<Object>} Object with google and outlook calendar links
 */
export async function getCalendarLinks(mealId) {
  const res = await fetch(`${API_BASE_URL}/meals/${mealId}/calendar-links`, {
    method: 'GET',
    headers: authHeaders(),
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to fetch calendar links');
  return data;
}
