import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from '../../app/services/api';
import { usersApi } from '../../app/services/users-api';

vi.mock('../../app/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockedApi = vi.mocked(api);

describe('usersApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getAll calls GET /users with params', () => {
    const params = { role: 'admin' };
    usersApi.getAll(params);
    expect(mockedApi.get).toHaveBeenCalledWith('/users', { params });
  });

  it('getById calls GET /users/:id', () => {
    usersApi.getById('u1');
    expect(mockedApi.get).toHaveBeenCalledWith('/users/u1');
  });

  it('create calls POST /users with data', () => {
    const data = { email: 'new@scm.com', role: 'vendor' };
    usersApi.create(data);
    expect(mockedApi.post).toHaveBeenCalledWith('/users', data);
  });

  it('update calls PATCH /users/:id with data', () => {
    const data = { role: 'admin' };
    usersApi.update('u1', data);
    expect(mockedApi.patch).toHaveBeenCalledWith('/users/u1', data);
  });

  it('delete calls DELETE /users/:id', () => {
    usersApi.delete('u1');
    expect(mockedApi.delete).toHaveBeenCalledWith('/users/u1');
  });
});
