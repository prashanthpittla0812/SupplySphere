import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from '../../app/services/api';
import { warehousesApi } from '../../app/services/warehouses-api';

vi.mock('../../app/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockedApi = vi.mocked(api);

describe('warehousesApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getAll calls GET /warehouses with params', () => {
    const params = { city: 'NYC' };
    warehousesApi.getAll(params);
    expect(mockedApi.get).toHaveBeenCalledWith('/warehouses', { params });
  });

  it('getById calls GET /warehouses/:id', () => {
    warehousesApi.getById('w1');
    expect(mockedApi.get).toHaveBeenCalledWith('/warehouses/w1');
  });

  it('create calls POST /warehouses with data', () => {
    const data = { name: 'Main Warehouse', location: 'NYC' };
    warehousesApi.create(data);
    expect(mockedApi.post).toHaveBeenCalledWith('/warehouses', data);
  });

  it('update calls PATCH /warehouses/:id with data', () => {
    const data = { name: 'Updated Warehouse' };
    warehousesApi.update('w1', data);
    expect(mockedApi.patch).toHaveBeenCalledWith('/warehouses/w1', data);
  });

  it('delete calls DELETE /warehouses/:id', () => {
    warehousesApi.delete('w1');
    expect(mockedApi.delete).toHaveBeenCalledWith('/warehouses/w1');
  });
});
