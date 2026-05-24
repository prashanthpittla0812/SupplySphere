import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from '../../app/services/api';

describe('api service', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('should add Bearer token from localStorage', async () => {
    localStorage.setItem('auth-storage', JSON.stringify({ state: { token: 'my-token' } }));
    const config = { headers: {} } as any;
    const result = await (api as any).interceptors.request.handlers[0].fulfilled(config);
    expect(result.headers.Authorization).toBe('Bearer my-token');
  });

  it('should not add Authorization when no token in storage', async () => {
    localStorage.setItem('auth-storage', JSON.stringify({ state: {} }));
    const config = { headers: {} } as any;
    const result = await (api as any).interceptors.request.handlers[0].fulfilled(config);
    expect(result.headers.Authorization).toBeUndefined();
  });

  it('should not add Authorization when no auth-storage key', async () => {
    const config = { headers: {} } as any;
    const result = await (api as any).interceptors.request.handlers[0].fulfilled(config);
    expect(result.headers.Authorization).toBeUndefined();
  });

  it('should have correct base URL', () => {
    expect(api.defaults.baseURL).toBe('/api');
  });

  it('should have JSON content type', () => {
    expect(api.defaults.headers['Content-Type']).toBe('application/json');
  });

  it('should reject non-401 errors through response interceptor', async () => {
    const error = { response: { status: 500 }, config: {} };
    await expect(
      (api as any).interceptors.response.handlers[0].rejected(error)
    ).rejects.toEqual(error);
  });

  it('should reject 401 on retried requests', async () => {
    const error = { response: { status: 401 }, config: { _retry: true } };
    await expect(
      (api as any).interceptors.response.handlers[0].rejected(error)
    ).rejects.toEqual(error);
  });
});
