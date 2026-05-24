import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAuthStore } from '../../app/store/auth-store';
import api from '../../app/services/api';

vi.mock('../../app/services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe('authStore', () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({ user: null, token: null, isAuthenticated: false });
  });

  it('should have initial state', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('login() should set user and token', async () => {
    const mockUser = { id: '1', email: 'test@scm.com', name: 'Test User', role: 'admin' as const };
    const mockResponse = {
      data: {
        data: {
          user: mockUser,
          tokens: { accessToken: 'access-123', refreshToken: 'refresh-456' },
        },
      },
    };
    vi.mocked(api.post).mockResolvedValueOnce(mockResponse);

    await useAuthStore.getState().login('test@scm.com', 'pass123');

    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.token).toBe('access-123');
    expect(state.isAuthenticated).toBe(true);
    expect(api.post).toHaveBeenCalledWith('/auth/login', {
      email: 'test@scm.com',
      password: 'pass123',
    });
  });

  it('logout() should clear user and token', async () => {
    useAuthStore.setState({
      user: { id: '1', email: 'test@scm.com', name: 'Test', role: 'admin' },
      token: 'tok-123',
      isAuthenticated: true,
    });
    vi.mocked(api.post).mockResolvedValueOnce({});

    await useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('logout() should clear state even when API fails', async () => {
    useAuthStore.setState({
      user: { id: '1', email: 'test@scm.com', name: 'Test', role: 'admin' },
      token: 'tok-123',
      isAuthenticated: true,
    });
    vi.mocked(api.post).mockRejectedValueOnce(new Error('Network error'));

    await useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('setUser() should update the user', () => {
    const newUser = { id: '2', email: 'new@scm.com', name: 'New User', role: 'vendor' as const };
    useAuthStore.getState().setUser(newUser);

    expect(useAuthStore.getState().user).toEqual(newUser);
  });

  it('refreshToken sets new token on success', async () => {
    useAuthStore.setState({
      user: { id: '1', email: 'test@scm.com', name: 'Test', role: 'admin' },
      token: 'old-token',
      isAuthenticated: true,
    });

    const mockResponse = {
      data: { data: { accessToken: 'new-access', refreshToken: 'new-refresh' } },
    };
    vi.mocked(api.post).mockResolvedValueOnce(mockResponse);

    await useAuthStore.getState().refreshToken();

    expect(useAuthStore.getState().token).toBe('new-access');
    expect(useAuthStore.getState().isAuthenticated).toBe(true);
  });

  it('fetchMe sets user on success', async () => {
    const mockUser = { id: '1', email: 'user@scm.com', name: 'User', role: 'admin' };
    vi.mocked(api.get).mockResolvedValueOnce({
      data: { data: mockUser },
    });

    await useAuthStore.getState().fetchMe();

    expect(useAuthStore.getState().user).toEqual(mockUser);
    expect(useAuthStore.getState().isAuthenticated).toBe(true);
  });

  it('refreshToken clears state on failure', async () => {
    useAuthStore.setState({
      user: { id: '1', email: 'test@scm.com', name: 'Test', role: 'admin' },
      token: 'old-token',
      isAuthenticated: true,
    });

    vi.mocked(api.post).mockRejectedValueOnce(new Error('Refresh failed'));

    await useAuthStore.getState().refreshToken();

    expect(useAuthStore.getState().user).toBeNull();
    expect(useAuthStore.getState().token).toBeNull();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });

  it('fetchMe clears state on failure', async () => {
    useAuthStore.setState({
      user: { id: '1', email: 'user@scm.com', name: 'User', role: 'admin' },
      token: 'tok',
      isAuthenticated: true,
    });

    vi.mocked(api.get).mockRejectedValueOnce(new Error('Fetch failed'));

    await useAuthStore.getState().fetchMe();

    expect(useAuthStore.getState().user).toBeNull();
    expect(useAuthStore.getState().token).toBeNull();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });
});
