import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from '../../app/services/api';
import { invoicesApi } from '../../app/services/invoices-api';

vi.mock('../../app/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockedApi = vi.mocked(api);

describe('invoicesApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getAll calls GET /invoices with params', () => {
    const params = { status: 'unpaid' };
    invoicesApi.getAll(params);
    expect(mockedApi.get).toHaveBeenCalledWith('/invoices', { params });
  });

  it('getById calls GET /invoices/:id', () => {
    invoicesApi.getById('inv1');
    expect(mockedApi.get).toHaveBeenCalledWith('/invoices/inv1');
  });

  it('create calls POST /invoices with data', () => {
    const data = { orderId: 'o1', amount: 100 };
    invoicesApi.create(data);
    expect(mockedApi.post).toHaveBeenCalledWith('/invoices', data);
  });

  it('update calls PATCH /invoices/:id with data', () => {
    const data = { status: 'paid' };
    invoicesApi.update('inv1', data);
    expect(mockedApi.patch).toHaveBeenCalledWith('/invoices/inv1', data);
  });

  it('delete calls DELETE /invoices/:id', () => {
    invoicesApi.delete('inv1');
    expect(mockedApi.delete).toHaveBeenCalledWith('/invoices/inv1');
  });

  it('markPaid calls PATCH /invoices/:id/pay', () => {
    invoicesApi.markPaid('inv1');
    expect(mockedApi.patch).toHaveBeenCalledWith('/invoices/inv1/pay');
  });

  it('downloadPdf calls GET /invoices/:id/pdf with blob responseType', () => {
    invoicesApi.downloadPdf('inv1');
    expect(mockedApi.get).toHaveBeenCalledWith('/invoices/inv1/pdf', { responseType: 'blob' });
  });
});
