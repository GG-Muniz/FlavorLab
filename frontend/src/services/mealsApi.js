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

export async function getCalendarLinks(mealId) {
  const res = await fetch(`${API_BASE_URL}/meals/${mealId}/calendar-links`, {
    method: 'GET',
    headers: authHeaders(),
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to fetch calendar links');
  return data;
}

export async function logMealForToday(mealId) {
  const res = await fetch(`${API_BASE_URL}/meals/${mealId}/log`, {
    method: 'POST',
    headers: authHeaders(),
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to log meal for today');
  return data;
}

export async function logManualCalories(mealType, calories) {
  const res = await fetch(`${API_BASE_URL}/meals/log-manual`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ meal_type: mealType, calories })
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to log manual calories');
  return data;
}

export async function setCalorieGoal(goalCalories) {
  const res = await fetch(`${API_BASE_URL}/calorie/goal`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify({ goal_calories: goalCalories })
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to set calorie goal');
  return data;
}

export async function getDailySummary() {
  const res = await fetch(`${API_BASE_URL}/users/me/daily-summary`, {
    method: 'GET',
    headers: authHeaders(),
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to fetch daily summary');
  return data;
}

export async function deleteLoggedMeal(mealId) {
  const res = await fetch(`${API_BASE_URL}/meals/${mealId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to delete logged meal');
  return data;
}

export async function updateLoggedMeal(mealId, mealType, calories) {
  const res = await fetch(`${API_BASE_URL}/meals/${mealId}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify({ meal_type: mealType, calories })
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to update logged meal');
  return data;
}

export async function fetchNutritionSummaryForDate(date) {
  const res = await fetch(`${API_BASE_URL}/meals/summary/${date}`, {
    method: 'GET',
    headers: authHeaders(),
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to fetch nutrition summary');
  return data;
}

export async function fetchMealsForDate(date) {
  const allLoggedMeals = await getMeals('logged');
  return allLoggedMeals.filter(meal => meal.date_logged === date);
}