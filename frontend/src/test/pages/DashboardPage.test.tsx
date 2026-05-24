import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { DashboardPage } from '../../app/pages/dashboard';
import { analyticsApi } from '../../app/services/analytics-api';

vi.mock('../../app/services/analytics-api', () => ({
  analyticsApi: {
    getDashboard: vi.fn(),
    getRevenue: vi.fn(),
    getOrderStatus: vi.fn(),
  },
}));

const mockStats = {
  totalRevenue: 50000,
  revenueChange: 12,
  totalOrders: 150,
  ordersChange: -5,
  activeShipments: 30,
  shipmentsChange: 8,
  lowStockItems: 12,
  stockChange: -3,
};

const mockRevenue = [
  { month: 'Jan', revenue: 10000 },
  { month: 'Feb', revenue: 15000 },
];

const mockOrderStatus = [
  { name: 'Pending', value: 10 },
  { name: 'Shipped', value: 20 },
];

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state initially', () => {
    vi.mocked(analyticsApi.getDashboard).mockReturnValue(new Promise(() => {}));
    vi.mocked(analyticsApi.getRevenue).mockReturnValue(new Promise(() => {}));
    vi.mocked(analyticsApi.getOrderStatus).mockReturnValue(new Promise(() => {}));

    render(<DashboardPage />);

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(
      screen.getByText('Overview of your supply chain operations')
    ).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /retry/i })).not.toBeInTheDocument();
  });

  it('renders stat cards and charts after loading', async () => {
    vi.mocked(analyticsApi.getDashboard).mockResolvedValue({ data: { data: mockStats } });
    vi.mocked(analyticsApi.getRevenue).mockResolvedValue({ data: { data: mockRevenue } });
    vi.mocked(analyticsApi.getOrderStatus).mockResolvedValue({ data: { data: mockOrderStatus } });

    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('Total Revenue')).toBeInTheDocument();
    });

    expect(screen.getByText('Total Revenue')).toBeInTheDocument();
    expect(screen.getByText('Total Orders')).toBeInTheDocument();
    expect(screen.getByText('Active Shipments')).toBeInTheDocument();
    expect(screen.getByText('Low Stock Items')).toBeInTheDocument();

    expect(screen.getByText('$50,000')).toBeInTheDocument();
    expect(screen.getByText('150')).toBeInTheDocument();
    expect(screen.getByText('30')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();

    expect(screen.getByText('Revenue Trend')).toBeInTheDocument();
    expect(screen.getByText('Order Status Distribution')).toBeInTheDocument();
    expect(screen.getByText('Monthly Revenue Comparison')).toBeInTheDocument();
  });

  it('shows error state on API failure', async () => {
    vi.mocked(analyticsApi.getDashboard).mockRejectedValue(new Error('API Error'));
    vi.mocked(analyticsApi.getRevenue).mockRejectedValue(new Error('API Error'));
    vi.mocked(analyticsApi.getOrderStatus).mockRejectedValue(new Error('API Error'));

    render(<DashboardPage />);

    await waitFor(() => {
      expect(
        screen.getByText('Failed to load dashboard data')
      ).toBeInTheDocument();
    });

    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });
});
