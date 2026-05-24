import api from './api';

export interface LoginResponse {
  user: { id: string; email: string; name: string; role: string; avatar?: string };
  tokens: { accessToken: string; refreshToken: string };
}

export const authApi = {
  login: (email: string, password: string) => api.post<{ success: boolean; data: LoginResponse }>('/auth/login', { email, password }),
  register: (data: { email: string; password: string; name: string; role?: string }) => api.post('/auth/register', data),
  logout: (refreshToken: string) => api.post('/auth/logout', { refreshToken }),
  refreshToken: (refreshToken: string) => api.post('/auth/refresh-token', { refreshToken }),
  forgotPassword: (email: string) => api.post('/auth/forgot-password', { email }),
  resetPassword: (token: string, password: string) => api.post('/auth/reset-password', { token, password }),
  getMe: () => api.get('/auth/me'),
};
