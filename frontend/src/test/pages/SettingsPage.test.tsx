import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SettingsPage } from '../../app/pages/settings';
import { MemoryRouter } from 'react-router';
import { toast } from 'sonner';

const mockSetUser = vi.hoisted(() => vi.fn());
const mockLogin = vi.hoisted(() => vi.fn());

vi.mock('../../app/store/auth-store', () => ({
  useAuthStore: (selector: (s: any) => any) =>
    selector({ user: { id: '1', name: 'Admin User', email: 'admin@scm.com', role: 'admin' }, setUser: mockSetUser }),
}));

vi.mock('../../app/services/auth-api', () => ({
  authApi: { login: mockLogin },
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

describe('SettingsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders settings page with tabs', () => {
    render(
      <MemoryRouter>
        <SettingsPage />
      </MemoryRouter>
    );

    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
    expect(screen.getByText('Notifications')).toBeInTheDocument();
    expect(screen.getByText('Security')).toBeInTheDocument();
  });

  it('shows user profile info', () => {
    render(
      <MemoryRouter>
        <SettingsPage />
      </MemoryRouter>
    );

    expect(screen.getByDisplayValue('Admin User')).toBeInTheDocument();
    expect(screen.getByDisplayValue('admin@scm.com')).toBeInTheDocument();
  });

  it('saves notification preferences', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <SettingsPage />
      </MemoryRouter>
    );

    await user.click(screen.getByText('Notifications'));

    await user.click(screen.getByRole('button', { name: /save preferences/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('Notification preferences saved');
    });
  });

  it('updates password', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <SettingsPage />
      </MemoryRouter>
    );

    await user.click(screen.getByText('Security'));

    await user.click(screen.getByRole('button', { name: /update password/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('Password updated successfully');
    });
  });

  it('saves profile settings', async () => {
    mockLogin.mockResolvedValue({
      data: { data: { user: { id: '1', name: 'Admin', email: 'admin@scm.com', role: 'admin' } } },
    });

    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <SettingsPage />
      </MemoryRouter>
    );

    await user.click(screen.getByRole('button', { name: /save changes/i }));

    await waitFor(() => {
      expect(mockSetUser).toHaveBeenCalled();
    });

    expect(toast.success).toHaveBeenCalledWith('Profile updated successfully');
  });
});
