import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from '../../app/services/api';
import { authApi } from '../../app/services/auth-api';

vi.mock('../../app/services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe('authApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('login calls POST /auth/login with email and password', () => {
    authApi.login('admin@scm.com', 'secret');
    expect(api.post).toHaveBeenCalledWith('/auth/login', {
      email: 'admin@scm.com',
      password: 'secret',
    });
  });

  it('register calls POST /auth/register with data', () => {
    const data = { email: 'new@scm.com', password: 'pass', name: 'New', role: 'vendor' };
    authApi.register(data);
    expect(api.post).toHaveBeenCalledWith('/auth/register', data);
  });

  it('refreshToken calls POST /auth/refresh-token', () => {
    authApi.refreshToken('refresh-val');
    expect(api.post).toHaveBeenCalledWith('/auth/refresh-token', {
      refreshToken: 'refresh-val',
    });
  });

  it('logout calls POST /auth/logout', () => {
    authApi.logout('my-refresh');
    expect(api.post).toHaveBeenCalledWith('/auth/logout', {
      refreshToken: 'my-refresh',
    });
  });

  it('forgotPassword calls POST /auth/forgot-password', () => {
    authApi.forgotPassword('user@scm.com');
    expect(api.post).toHaveBeenCalledWith('/auth/forgot-password', {
      email: 'user@scm.com',
    });
  });

  it('resetPassword calls POST /auth/reset-password', () => {
    authApi.resetPassword('tok', 'newpass');
    expect(api.post).toHaveBeenCalledWith('/auth/reset-password', {
      token: 'tok',
      password: 'newpass',
    });
  });

  it('getMe calls GET /auth/me', () => {
    authApi.getMe();
    expect(api.get).toHaveBeenCalledWith('/auth/me');
  });
});
