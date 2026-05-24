import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WarehousesPage } from '../../app/pages/warehouses';
import { warehousesApi } from '../../app/services/warehouses-api';

vi.mock('../../app/services/warehouses-api', () => ({
  warehousesApi: { getAll: vi.fn() },
}));

describe('WarehousesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state initially', () => {
    vi.mocked(warehousesApi.getAll).mockReturnValue(new Promise(() => {}));

    render(<WarehousesPage />);

    expect(screen.getByText('Warehouses')).toBeInTheDocument();
    expect(screen.getByText('Manage your warehouse facilities')).toBeInTheDocument();
  });

  it('renders warehouse cards after loading', async () => {
    const mockWarehouses = [
      { id: '1', name: 'Main Warehouse', location: 'New York', status: 'operational', currentStock: 500, capacity: 1000 },
      { id: '2', name: 'Secondary Hub', location: 'Los Angeles', status: 'maintenance', currentStock: 200, capacity: 800 },
    ];

    vi.mocked(warehousesApi.getAll).mockResolvedValue({ data: { data: mockWarehouses } });

    render(<WarehousesPage />);

    await waitFor(() => {
      expect(screen.getByText('Main Warehouse')).toBeInTheDocument();
    });

    expect(screen.getByText('Secondary Hub')).toBeInTheDocument();
    expect(screen.getByText('New York')).toBeInTheDocument();
    expect(screen.getByText('Los Angeles')).toBeInTheDocument();
    expect(screen.getByText('Add Warehouse')).toBeInTheDocument();
  });

  it('shows error state on API failure', async () => {
    vi.mocked(warehousesApi.getAll).mockRejectedValue(new Error('Network error'));

    render(<WarehousesPage />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load warehouses')).toBeInTheDocument();
    });

    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('retries fetch on retry button click', async () => {
    vi.mocked(warehousesApi.getAll).mockRejectedValueOnce(new Error('Network error'));
    vi.mocked(warehousesApi.getAll).mockResolvedValueOnce({ data: { data: [] } });

    const user = userEvent.setup();

    render(<WarehousesPage />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load warehouses')).toBeInTheDocument();
    });

    await user.click(screen.getByRole('button', { name: /retry/i }));

    await waitFor(() => {
      expect(screen.queryByText('Failed to load warehouses')).not.toBeInTheDocument();
    });
  });
});
