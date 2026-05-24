import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from '../../app/services/api';
import { ordersApi } from '../../app/services/orders-api';

vi.mock('../../app/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockedApi = vi.mocked(api);

describe('ordersApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getAll calls GET /orders with params', () => {
    const params = { status: 'pending' };
    ordersApi.getAll(params);
    expect(mockedApi.get).toHaveBeenCalledWith('/orders', { params });
  });

  it('getById calls GET /orders/:id', () => {
    ordersApi.getById('o1');
    expect(mockedApi.get).toHaveBeenCalledWith('/orders/o1');
  });

  it('create calls POST /orders with data', () => {
    const data = { productId: 'p1', quantity: 5 };
    ordersApi.create(data);
    expect(mockedApi.post).toHaveBeenCalledWith('/orders', data);
  });

  it('update calls PATCH /orders/:id with data', () => {
    const data = { status: 'shipped' };
    ordersApi.update('o1', data);
    expect(mockedApi.patch).toHaveBeenCalledWith('/orders/o1', data);
  });

  it('delete calls DELETE /orders/:id', () => {
    ordersApi.delete('o1');
    expect(mockedApi.delete).toHaveBeenCalledWith('/orders/o1');
  });

  it('approve calls PATCH /orders/:id/approve', () => {
    ordersApi.approve('o1');
    expect(mockedApi.patch).toHaveBeenCalledWith('/orders/o1/approve');
  });

  it('reject calls PATCH /orders/:id/reject', () => {
    ordersApi.reject('o1');
    expect(mockedApi.patch).toHaveBeenCalledWith('/orders/o1/reject');
  });
});
