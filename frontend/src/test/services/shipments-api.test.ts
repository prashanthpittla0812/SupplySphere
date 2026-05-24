import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from '../../app/services/api';
import { shipmentsApi } from '../../app/services/shipments-api';

vi.mock('../../app/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockedApi = vi.mocked(api);

describe('shipmentsApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getAll calls GET /shipments with params', () => {
    const params = { status: 'in_transit' };
    shipmentsApi.getAll(params);
    expect(mockedApi.get).toHaveBeenCalledWith('/shipments', { params });
  });

  it('getById calls GET /shipments/:id', () => {
    shipmentsApi.getById('s1');
    expect(mockedApi.get).toHaveBeenCalledWith('/shipments/s1');
  });

  it('create calls POST /shipments with data', () => {
    const data = { orderId: 'o1', carrier: 'UPS' };
    shipmentsApi.create(data);
    expect(mockedApi.post).toHaveBeenCalledWith('/shipments', data);
  });

  it('update calls PATCH /shipments/:id with data', () => {
    const data = { status: 'delivered' };
    shipmentsApi.update('s1', data);
    expect(mockedApi.patch).toHaveBeenCalledWith('/shipments/s1', data);
  });

  it('delete calls DELETE /shipments/:id', () => {
    shipmentsApi.delete('s1');
    expect(mockedApi.delete).toHaveBeenCalledWith('/shipments/s1');
  });

  it('getTracking calls GET /shipments/:id/tracking', () => {
    shipmentsApi.getTracking('s1');
    expect(mockedApi.get).toHaveBeenCalledWith('/shipments/s1/tracking');
  });
});
