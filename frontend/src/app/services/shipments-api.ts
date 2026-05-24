import api from './api';

export const shipmentsApi = {
  getAll: (params?: Record<string, unknown>) => api.get('/shipments', { params }),
  getById: (id: string) => api.get(`/shipments/${id}`),
  create: (data: Record<string, unknown>) => api.post('/shipments', data),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/shipments/${id}`, data),
  delete: (id: string) => api.delete(`/shipments/${id}`),
  getTracking: (id: string) => api.get(`/shipments/${id}/tracking`),
};
