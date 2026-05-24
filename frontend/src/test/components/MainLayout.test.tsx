import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { MainLayout } from '../../app/components/layout/main-layout';

vi.mock('../../app/components/layout/sidebar', () => ({
  Sidebar: () => <div>Mock Sidebar</div>,
}));

vi.mock('../../app/components/layout/header', () => ({
  Header: () => <header>Mock Header</header>,
}));

describe('MainLayout', () => {
  it('renders sidebar, header, and outlet', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <MainLayout />
      </MemoryRouter>
    );

    expect(screen.getByText('Mock Sidebar')).toBeInTheDocument();
    expect(screen.getByText('Mock Header')).toBeInTheDocument();
  });
});
