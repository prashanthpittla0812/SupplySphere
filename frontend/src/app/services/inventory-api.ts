import api from './api';

export const inventoryApi = {
  getAll: (params?: Record<string, unknown>) => api.get('/inventory', { params }),
  getById: (id: string) => api.get(`/inventory/${id}`),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/inventory/${id}`, data),
  adjustStock: (id: string, data: { quantity: number; type: 'add' | 'subtract' }) => api.patch(`/inventory/${id}/stock`, data),
  getLowStock: () => api.get('/inventory', { params: { status: 'LOW_STOCK' } }),
};
