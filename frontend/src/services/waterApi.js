// waterApi.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

function authHeaders() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
}

async function safeJson(res) {
  const text = await res.text();
  try { return text ? JSON.parse(text) : {}; } catch { return {}; }
}

export async function updateDailyWaterGoal(goalMl) {
  const res = await fetch(`${API_BASE_URL}/water/goal`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify({ goal_ml: goalMl })
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to update water goal');
  return data;
}

export async function logWaterIntake(volumeMl) {
  const res = await fetch(`${API_BASE_URL}/water/intake`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ volume_ml: volumeMl })
  });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to log water intake');
  return data;
}

export async function fetchWaterSummary(dateStr) {
  const url = dateStr ? `${API_BASE_URL}/water/summary?target_date=${dateStr}` : `${API_BASE_URL}/water/summary`;
  const res = await fetch(url, { headers: authHeaders() });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data?.detail || 'Failed to fetch water summary');
  return data;
}

export default { updateDailyWaterGoal, logWaterIntake, fetchWaterSummary };


