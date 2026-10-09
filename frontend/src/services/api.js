const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

async function request(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const baseUrl = API_BASE_URL.replace(/\/$/, '');
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

  const response = await fetch(`${baseUrl}${cleanEndpoint}`, {
    ...options,
    credentials: 'include',
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
  logout: () => request('/auth/logout', { method: 'POST' }),
  getMe: () => request('/auth/me'),

  // User Dashboard
  getDashboard: () => request('/user/dashboard'),

  // Challenges
  getChallenges: () => request('/challenges'),
  getChallengeDetail: (id) => request(`/challenges/${id}`),
  startChallenge: (id) => request(`/challenges/${id}/start`, { method: 'POST' }),
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

