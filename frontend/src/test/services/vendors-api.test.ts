import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from '../../app/services/api';
import { vendorsApi } from '../../app/services/vendors-api';

vi.mock('../../app/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockedApi = vi.mocked(api);

describe('vendorsApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getAll calls GET /vendors with params', () => {
    const params = { page: 1 };
    vendorsApi.getAll(params);
    expect(mockedApi.get).toHaveBeenCalledWith('/vendors', { params });
  });

  it('getById calls GET /vendors/:id', () => {
    vendorsApi.getById('v1');
    expect(mockedApi.get).toHaveBeenCalledWith('/vendors/v1');
  });

  it('create calls POST /vendors with data', () => {
    const data = { name: 'Vendor Inc' };
    vendorsApi.create(data);
    expect(mockedApi.post).toHaveBeenCalledWith('/vendors', data);
  });

  it('update calls PATCH /vendors/:id with data', () => {
    const data = { name: 'Updated' };
    vendorsApi.update('v1', data);
    expect(mockedApi.patch).toHaveBeenCalledWith('/vendors/v1', data);
  });

  it('delete calls DELETE /vendors/:id', () => {
    vendorsApi.delete('v1');
    expect(mockedApi.delete).toHaveBeenCalledWith('/vendors/v1');
  });

  it('approve calls PATCH /vendors/:id/approve', () => {
    vendorsApi.approve('v1');
    expect(mockedApi.patch).toHaveBeenCalledWith('/vendors/v1/approve');
  });

  it('reject calls PATCH /vendors/:id/reject', () => {
    vendorsApi.reject('v1');
    expect(mockedApi.patch).toHaveBeenCalledWith('/vendors/v1/reject');
  });
});
