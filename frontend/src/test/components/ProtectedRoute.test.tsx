import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { ProtectedRoute } from '../../app/routes';

const mockUseAuthStore = vi.hoisted(() => vi.fn());

vi.mock('../../app/store/auth-store', () => ({
  useAuthStore: (selector: (s: any) => any) => mockUseAuthStore(selector),
}));

describe('ProtectedRoute', () => {
  it('redirects to /login when not authenticated', () => {
    mockUseAuthStore.mockImplementation((selector: (s: any) => any) =>
      selector({ isAuthenticated: false })
    );

    render(
      <MemoryRouter>
        <ProtectedRoute>
          <div>Secret Content</div>
        </ProtectedRoute>
      </MemoryRouter>
    );

    expect(screen.queryByText('Secret Content')).not.toBeInTheDocument();
  });

  it('renders children when authenticated', () => {
    mockUseAuthStore.mockImplementation((selector: (s: any) => any) =>
      selector({ isAuthenticated: true })
    );

    render(
      <MemoryRouter>
        <ProtectedRoute>
          <div>Secret Content</div>
        </ProtectedRoute>
      </MemoryRouter>
    );

    expect(screen.getByText('Secret Content')).toBeInTheDocument();
  });
});
