// nutritionApi.js
// Adapters for backend nutrition endpoints

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

function authHeaders() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function safeJson(res) {
  const text = await res.text();
  try { return text ? JSON.parse(text) : {}; } catch { return {}; }
}

export async function fetchNutritionGoals() {
  const res = await fetch(`${API_BASE_URL}/users/me/nutrition-goals`, { headers: { ...authHeaders() } });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to fetch nutrition goals');
  // Expected: { calories, protein_g, carbs_g, fat_g }
  return {
    calories: data.calories ?? 2000,
    proteinTarget: data.protein_g ?? 150,
    carbsTarget: data.carbs_g ?? 250,
    fatTarget: data.fat_g ?? 67,
  };
}

export async function fetchDailySummary(dateStr) {
  const res = await fetch(`${API_BASE_URL}/meals/summary/${dateStr}`, { headers: { ...authHeaders() } });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to fetch daily summary');
  // Expected: { total_calories, total_protein_g, total_carbs_g, total_fat_g }
  return {
    calories: data.total_calories ?? 0,
    protein: data.total_protein_g ?? 0,
    carbs: data.total_carbs_g ?? 0,
    fat: data.total_fat_g ?? 0,
  };
}
