// Simple auth API wrapper for backend integration

// Use relative API path so Vite dev server proxy handles CORS transparently
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
export const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
export function absoluteUrl(path) {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `${BACKEND_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
}

async function parseJson(response) {
  const text = await response.text();
  try {
    return text ? JSON.parse(text) : {};
  } catch {
    return {};
  }
}

export async function loginUser(email, password) {
  const normalizedEmail = (email || '').trim().toLowerCase();
  const response = await fetch(`${API_BASE_URL}/users/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    },
    body: new URLSearchParams({ email: normalizedEmail, password })
  });

  const data = await parseJson(response);

  if (!response.ok) {
    const message = data?.detail || 'Login failed';
    throw new Error(typeof message === 'string' ? message : 'Login failed');
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
  const response = await fetch(`${API_BASE_URL}/users/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email: normalizedEmail, password })
  });

  const data = await parseJson(response);
  if (!response.ok) {
    const message = data?.detail || 'Registration failed';
    throw new Error(typeof message === 'string' ? message : 'Registration failed');
  }
  return data;
}

export async function getCurrentUser(token) {
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const data = await parseJson(response);
  if (!response.ok) {
    const message = data?.detail || 'Failed to load user';
    throw new Error(typeof message === 'string' ? message : 'Failed to load user');
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
    const message = data?.detail || 'Failed to update profile';
    throw new Error(typeof message === 'string' ? message : 'Failed to update profile');
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
    const message = data?.detail || 'Failed to request password reset';
    throw new Error(typeof message === 'string' ? message : 'Failed to request password reset');
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
    const message = data?.detail || 'Failed to reset password';
    throw new Error(typeof message === 'string' ? message : 'Failed to reset password');
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
    const message = data?.detail || 'Failed to upload avatar';
    throw new Error(typeof message === 'string' ? message : 'Failed to upload avatar');
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
    const message = data?.detail || 'Failed to change password';
    throw new Error(typeof message === 'string' ? message : 'Failed to change password');
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
    const message = data?.detail || 'Failed to delete account';
    throw new Error(typeof message === 'string' ? message : 'Failed to delete account');
  }
  return data;
}

