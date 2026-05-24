import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { Sidebar } from '../../app/components/layout/sidebar';

const mockAuthStore = vi.hoisted(() => ({ user: null, logout: vi.fn() }));

vi.mock('../../app/store/auth-store', () => ({
  useAuthStore: (selector?: (s: any) => any) =>
    selector ? selector(mockAuthStore) : mockAuthStore,
}));

describe('Sidebar', () => {
  it('renders navigation items for admin user', () => {
    mockAuthStore.user = { name: 'Admin', email: 'admin@scm.com', role: 'admin' };

    render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Vendors')).toBeInTheDocument();
    expect(screen.getByText('Reports')).toBeInTheDocument();
    expect(screen.getByText('User Management')).toBeInTheDocument();
    expect(screen.getByText('Billing')).toBeInTheDocument();
    expect(screen.getByText('SCM System')).toBeInTheDocument();
  });

  it('renders filtered navigation for vendor user', () => {
    mockAuthStore.user = { name: 'Vendor', email: 'vendor@scm.com', role: 'vendor' };

    render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Inventory')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.queryByText('Vendors')).not.toBeInTheDocument();
    expect(screen.queryByText('Reports')).not.toBeInTheDocument();
    expect(screen.queryByText('User Management')).not.toBeInTheDocument();
  });

  it('shows user info and logout button', () => {
    mockAuthStore.user = { name: 'Test User', email: 'test@scm.com', role: 'warehouse_manager' };

    render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>
    );

    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('test@scm.com')).toBeInTheDocument();
    expect(screen.getByText('warehouse manager')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });
});
