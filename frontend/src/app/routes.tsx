import { createBrowserRouter, Navigate } from 'react-router';
import { MainLayout } from './components/layout/main-layout';
import { LoginPage } from './pages/login';
import { RegisterPage } from './pages/register';
import { DashboardPage } from './pages/dashboard';
import { VendorsPage } from './pages/vendors';
import { InventoryPage } from './pages/inventory';
import { WarehousesPage } from './pages/warehouses';
import { OrdersPage } from './pages/orders';
import { ShipmentsPage } from './pages/shipments';
import { BillingPage } from './pages/billing';
import { ReportsPage } from './pages/reports';
import { UsersPage } from './pages/users';
import { SettingsPage } from './pages/settings';
import { useAuthStore } from './store/auth-store';

// Protected Route Component
export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <MainLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: 'vendors',
        element: <VendorsPage />,
      },
      {
        path: 'inventory',
        element: <InventoryPage />,
      },
      {
        path: 'warehouses',
        element: <WarehousesPage />,
      },
      {
        path: 'orders',
        element: <OrdersPage />,
      },
      {
        path: 'shipments',
        element: <ShipmentsPage />,
      },
      {
        path: 'billing',
        element: <BillingPage />,
      },
      {
        path: 'reports',
        element: <ReportsPage />,
      },
      {
        path: 'users',
        element: <UsersPage />,
      },
      {
        path: 'settings',
        element: <SettingsPage />,
      },
    ],
  },
]);
