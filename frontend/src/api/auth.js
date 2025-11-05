// Simple auth API wrapper for backend integration

// Use relative API path so Vite dev server proxy handles CORS transparently
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
export const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
export function absoluteUrl(path) {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `${BACKEND_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
}

async function fetchWithTimeout(url, options = {}, timeoutMs = 15000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    return res;
  } finally {
    clearTimeout(id);
  }
}

// Use Vite proxy first; if it fails or times out, fall back to absolute backend URL(s)
async function fetchWithProxyFallback(relativePath, options = {}, timeoutMs = 15000) {
  const rel = relativePath.startsWith('/') ? relativePath : `/${relativePath}`;
  const primaryUrl = `${API_BASE_URL}${rel.startsWith('/') ? rel : `/${rel}`}`;
  // Ensure fallback includes API prefix; reuse absoluteUrl to prepend backend host
  const fallbackUrl = absoluteUrl(`${API_BASE_URL}${rel}`);
  const extraFallbacks = [
    // Common local dev URLs (ordered by likelihood)
    `http://127.0.0.1:8000${API_BASE_URL}${rel}`,
    `http://localhost:8000${API_BASE_URL}${rel}`,
    `http://127.0.0.1:8001${API_BASE_URL}${rel}`,
    `http://localhost:8001${API_BASE_URL}${rel}`,
  ];

  try {
    const res = await fetchWithTimeout(primaryUrl, options, timeoutMs);
    // Fallback on 404/5xx that may indicate proxy not applied to this path
    if (res && res.ok) return res;
    if (res && [0, 404, 502, 503, 504].includes(res.status)) {
      try {
        const alt = await fetchWithTimeout(fallbackUrl, options, timeoutMs);
        if (alt && alt.ok) return alt;
      } catch (_) {}
      for (const url of extraFallbacks) {
        try {
          const r = await fetchWithTimeout(url, options, timeoutMs);
          if (r && r.ok) return r;
        } catch (_) {}
      }
      throw new Error('Backend unreachable at ' + fallbackUrl);
    }
    return res;
  } catch (_) {
    // Network error or timeout → try absolute backend
    const urls = [fallbackUrl, ...extraFallbacks];
    for (const url of urls) {
      try {
        const r = await fetchWithTimeout(url, options, timeoutMs);
        if (r && r.ok) return r;
      } catch (_) {}
    }
    throw new Error('Backend unreachable at ' + fallbackUrl);
  }
}

async function parseJson(response) {
  const text = await response.text();
  try {
    return text ? JSON.parse(text) : {};
  } catch {
    return {};
  }
}

function extractErrorMessage(detail, fallback = 'Request failed') {
  if (!detail) return fallback;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (!item) return null;
        if (typeof item === 'string') return item;
        if (typeof item === 'object') {
          return item.msg || item.message || item.detail || null;
        }
        return null;
      })
      .filter(Boolean);
    if (messages.length) {
      return messages.join('; ');
    }
  }
  if (typeof detail === 'object') {
    return detail.msg || detail.message || detail.detail || fallback;
  }
  return fallback;
}

export async function loginUser(email, password) {
  const normalizedEmail = (email || '').trim().toLowerCase();
  const response = await fetchWithProxyFallback('/users/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    },
    body: new URLSearchParams({ email: normalizedEmail, password })
  });

  const data = await parseJson(response);

  if (!response.ok) {
    const message = extractErrorMessage(data?.detail, 'Login failed');
    throw new Error(message);
  }

  // Expecting { access_token: string, token_type: 'bearer', user?: {...} }
  const token = data?.access_token;
  if (!token) {
    throw new Error('Login response missing access_token');
  }
  return { token, user: data?.user };
}

export async function registerUser(email, password) {
  const normalizedEmail = (email || '').trim().toLowerCase();
  const response = await fetchWithProxyFallback('/users/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email: normalizedEmail, password })
  });

  const data = await parseJson(response);
  if (!response.ok) {
    const message = extractErrorMessage(data?.detail, 'Registration failed');
    throw new Error(message);
  }
  return data;
}

export async function getCurrentUser(token) {
  const response = await fetchWithProxyFallback('/users/me', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const data = await parseJson(response);
  if (!response.ok) {
    const message = extractErrorMessage(data?.detail, 'Failed to load user');
    throw new Error(message);
  }
  return data;
}

export async function updateUserProfile(token, payload) {
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });
  const data = await parseJson(response);
  if (!response.ok) {
    const message = extractErrorMessage(data?.detail, 'Failed to update profile');
    throw new Error(message);
  }
  return data;
}

export function withAuthHeaders(token, extra = {}) {
  return {
    ...extra,
    headers: {
      ...(extra.headers || {}),
      'Authorization': `Bearer ${token}`
    }
  };
}

export async function requestPasswordReset(email) {
  const normalizedEmail = (email || '').trim().toLowerCase();
  const response = await fetch(`${API_BASE_URL}/users/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: normalizedEmail })
  });
  const data = await parseJson(response);
  if (!response.ok) {
    const message = extractErrorMessage(data?.detail, 'Failed to request password reset');
    throw new Error(message);
  }
  return data;
}

export async function resetPassword(token, newPassword) {
  const response = await fetch(`${API_BASE_URL}/users/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, new_password: newPassword })
  });
  const data = await parseJson(response);
  if (!response.ok) {
    const message = extractErrorMessage(data?.detail, 'Failed to reset password');
    throw new Error(message);
  }
  return data;
}

export async function uploadAvatar(token, file) {
  const form = new FormData();
  form.append('file', file);
  const response = await fetch(`${API_BASE_URL}/users/me/avatar`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: form
  });
  const data = await parseJson(response);
  if (!response.ok) {
    const message = extractErrorMessage(data?.detail, 'Failed to upload avatar');
    throw new Error(message);
  }
  return data;
}

export async function changePassword(token, currentPassword, newPassword) {
  const response = await fetch(`${API_BASE_URL}/users/me/change-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
  });
  const data = await parseJson(response);
  if (!response.ok) {
    const message = extractErrorMessage(data?.detail, 'Failed to change password');
    throw new Error(message);
  }
  return data;
}

export async function deleteMyAccount(token) {
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const data = await parseJson(response);
  if (!response.ok) {
    const message = extractErrorMessage(data?.detail, 'Failed to delete account');
    throw new Error(message);
  }
  return data;
}

