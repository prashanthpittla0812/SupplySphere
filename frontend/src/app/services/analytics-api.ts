import api from './api';

export const analyticsApi = {
  getDashboard: () => api.get('/analytics/dashboard'),
  getRevenue: () => api.get('/analytics/revenue'),
  getOrderStatus: () => api.get('/analytics/order-status'),
  getInventoryByCategory: () => api.get('/analytics/inventory-by-category'),
};
