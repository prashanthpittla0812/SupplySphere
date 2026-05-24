import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../services/api';

export type UserRole = 'admin' | 'warehouse_manager' | 'vendor' | 'delivery_personnel';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  avatar?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  refreshTokenValue: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  fetchMe: () => Promise<void>;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshTokenValue: null,
      isAuthenticated: false,
      login: async (email: string, password: string) => {
        const response = await api.post('/auth/login', { email, password });
        const { user, tokens } = response.data.data;
        set({ user, token: tokens.accessToken, refreshTokenValue: tokens.refreshToken, isAuthenticated: true });
      },
      logout: async () => {
        try {
          const { refreshTokenValue } = get();
          if (refreshTokenValue) {
            await api.post('/auth/logout', { refreshToken: refreshTokenValue });
          }
        } catch {
          // ignore logout errors
        }
        set({ user: null, token: null, refreshTokenValue: null, isAuthenticated: false });
      },
      refreshToken: async () => {
        try {
          const { refreshTokenValue } = get();
          if (!refreshTokenValue) throw new Error('No refresh token');
          const response = await api.post('/auth/refresh-token', { refreshToken: refreshTokenValue });
          const { accessToken, refreshToken: newRefreshToken } = response.data.data;
          set({ token: accessToken || newRefreshToken, refreshTokenValue: newRefreshToken || refreshTokenValue });
        } catch {
          set({ user: null, token: null, refreshTokenValue: null, isAuthenticated: false });
        }
      },
      fetchMe: async () => {
        try {
          const response = await api.get('/auth/me');
          set({ user: response.data.data, isAuthenticated: true });
        } catch {
          set({ user: null, token: null, refreshTokenValue: null, isAuthenticated: false });
        }
      },
      setUser: (user: User) => {
        set({ user });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshTokenValue: state.refreshTokenValue,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
