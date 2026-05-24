import api from './api';

export const vendorsApi = {
  getAll: (params?: Record<string, unknown>) => api.get('/vendors', { params }),
  getById: (id: string) => api.get(`/vendors/${id}`),
  create: (data: Record<string, unknown>) => api.post('/vendors', data),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/vendors/${id}`, data),
  delete: (id: string) => api.delete(`/vendors/${id}`),
  approve: (id: string) => api.patch(`/vendors/${id}/approve`),
  reject: (id: string) => api.patch(`/vendors/${id}/reject`),
};
