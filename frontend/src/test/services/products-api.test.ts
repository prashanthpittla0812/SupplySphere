import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from '../../app/services/api';
import { productsApi } from '../../app/services/products-api';

vi.mock('../../app/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockedApi = vi.mocked(api);

describe('productsApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getAll calls GET /products with params', () => {
    const params = { page: 1, limit: 10 };
    productsApi.getAll(params);
    expect(mockedApi.get).toHaveBeenCalledWith('/products', { params });
  });

  it('getAll calls GET /products without params', () => {
    productsApi.getAll();
    expect(mockedApi.get).toHaveBeenCalledWith('/products', { params: undefined });
  });

  it('getById calls GET /products/:id', () => {
    productsApi.getById('123');
    expect(mockedApi.get).toHaveBeenCalledWith('/products/123');
  });

  it('create calls POST /products with data', () => {
    const data = { name: 'Widget', price: 10 };
    productsApi.create(data);
    expect(mockedApi.post).toHaveBeenCalledWith('/products', data);
  });

  it('update calls PATCH /products/:id with data', () => {
    const data = { price: 15 };
    productsApi.update('123', data);
    expect(mockedApi.patch).toHaveBeenCalledWith('/products/123', data);
  });

  it('delete calls DELETE /products/:id', () => {
    productsApi.delete('123');
    expect(mockedApi.delete).toHaveBeenCalledWith('/products/123');
  });
});
