const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

export const getAuthToken = () => localStorage.getItem('cyberquest_token');
export const setAuthToken = (token) => localStorage.setItem('cyberquest_token', token);
export const removeAuthToken = () => localStorage.removeItem('cyberquest_token');

async function request(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const baseUrl = API_BASE_URL.replace(/\/$/, '');
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

  const response = await fetch(`${baseUrl}${cleanEndpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const error = new Error(data.error || data.message || 'API Request failed');
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

export const api = {
  // Auth
  register: (username, email, password) => 
    request('/auth/register', { method: 'POST', body: JSON.stringify({ username, email, password }) }),
  login: (account, password) => 
    request('/auth/login', { method: 'POST', body: JSON.stringify({ account, password }) }),
  getMe: () => request('/auth/me'),

  // User Dashboard
  getDashboard: () => request('/user/dashboard'),

  // Challenges
  getChallenges: () => request('/challenges'),
  getChallengeDetail: (id) => request(`/challenges/${id}`),
  submitFlag: (id, flag) => request(`/challenges/${id}/submit`, { method: 'POST', body: JSON.stringify({ flag }) }),

  // Hints
  unlockHint: (hintId) => request(`/hints/${hintId}/unlock`, { method: 'POST' }),

  // Leaderboard
  getLeaderboard: () => request('/leaderboard'),

  // Admin
  getAdminStats: () => request('/admin/stats'),
  getAdminChallenges: () => request('/admin/challenges'),
  createChallenge: (data) => request('/admin/challenges', { method: 'POST', body: JSON.stringify(data) }),
  updateChallenge: (id, data) => request(`/admin/challenges/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteChallenge: (id) => request(`/admin/challenges/${id}`, { method: 'DELETE' }),
  getAdminUsers: () => request('/admin/users'),
  deleteUser: (userId) => request(`/admin/users/${userId}`, { method: 'DELETE' }),
  clearAllPlayers: () => request('/admin/users/clear-players', { method: 'DELETE' }),
  getAdminSubmissions: () => request('/admin/submissions'),
};

