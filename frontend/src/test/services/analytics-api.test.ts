import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from '../../app/services/api';
import { analyticsApi } from '../../app/services/analytics-api';

vi.mock('../../app/services/api', () => ({
  default: {
    get: vi.fn(),
  },
}));

const mockedApi = vi.mocked(api);

describe('analyticsApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getDashboard calls GET /analytics/dashboard', () => {
    analyticsApi.getDashboard();
    expect(mockedApi.get).toHaveBeenCalledWith('/analytics/dashboard');
  });

  it('getRevenue calls GET /analytics/revenue', () => {
    analyticsApi.getRevenue();
    expect(mockedApi.get).toHaveBeenCalledWith('/analytics/revenue');
  });

  it('getOrderStatus calls GET /analytics/order-status', () => {
    analyticsApi.getOrderStatus();
    expect(mockedApi.get).toHaveBeenCalledWith('/analytics/order-status');
  });

  it('getInventoryByCategory calls GET /analytics/inventory-by-category', () => {
    analyticsApi.getInventoryByCategory();
    expect(mockedApi.get).toHaveBeenCalledWith('/analytics/inventory-by-category');
  });
});
