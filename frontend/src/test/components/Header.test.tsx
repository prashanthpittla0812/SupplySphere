import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router';
import { Header } from '../../app/components/layout/header';

const mockTheme = vi.hoisted(() => ({ theme: 'light', setTheme: vi.fn() }));

vi.mock('next-themes', () => ({
  useTheme: () => mockTheme,
}));

describe('Header', () => {
  it('renders search input', () => {
    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );
    expect(screen.getByPlaceholderText('Search orders, products, vendors...')).toBeInTheDocument();
  });

  it('renders two buttons', () => {
    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );
    expect(screen.getAllByRole('button')).toHaveLength(2);
  });

  it('toggles theme when theme button is clicked in light mode', async () => {
    mockTheme.theme = 'light';
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );

    const buttons = screen.getAllByRole('button');
    await user.click(buttons[0]);

    expect(mockTheme.setTheme).toHaveBeenCalledWith('dark');
  });

  it('shows sun icon in dark mode', () => {
    mockTheme.theme = 'dark';

    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );
  });

  it('toggles to light when clicked in dark mode', async () => {
    mockTheme.theme = 'dark';
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    );

    const buttons = screen.getAllByRole('button');
    await user.click(buttons[0]);

    expect(mockTheme.setTheme).toHaveBeenCalledWith('light');
  });
});
