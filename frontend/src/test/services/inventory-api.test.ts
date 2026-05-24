import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from '../../app/services/api';
import { inventoryApi } from '../../app/services/inventory-api';

vi.mock('../../app/services/api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
  },
}));

const mockedApi = vi.mocked(api);

describe('inventoryApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getAll calls GET /inventory with params', () => {
    const params = { category: 'raw' };
    inventoryApi.getAll(params);
    expect(mockedApi.get).toHaveBeenCalledWith('/inventory', { params });
  });

  it('getById calls GET /inventory/:id', () => {
    inventoryApi.getById('i1');
    expect(mockedApi.get).toHaveBeenCalledWith('/inventory/i1');
  });

  it('update calls PATCH /inventory/:id with data', () => {
    const data = { quantity: 100 };
    inventoryApi.update('i1', data);
    expect(mockedApi.patch).toHaveBeenCalledWith('/inventory/i1', data);
  });

  it('adjustStock calls PATCH /inventory/:id/stock with data', () => {
    const data = { quantity: 10, type: 'add' as const };
    inventoryApi.adjustStock('i1', data);
    expect(mockedApi.patch).toHaveBeenCalledWith('/inventory/i1/stock', data);
  });

  it('getLowStock calls GET /inventory with LOW_STOCK status', () => {
    inventoryApi.getLowStock();
    expect(mockedApi.get).toHaveBeenCalledWith('/inventory', { params: { status: 'LOW_STOCK' } });
  });
});
