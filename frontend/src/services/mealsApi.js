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
