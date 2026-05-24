// Mock data for the application

export const mockVendors = [
  { id: '1', name: 'Global Electronics Corp', email: 'contact@globalelec.com', phone: '+1-555-0101', status: 'active', rating: 4.5, totalOrders: 127 },
  { id: '2', name: 'TechSupply Industries', email: 'sales@techsupply.com', phone: '+1-555-0102', status: 'active', rating: 4.8, totalOrders: 89 },
  { id: '3', name: 'AutoParts International', email: 'info@autoparts.com', phone: '+1-555-0103', status: 'pending', rating: 4.2, totalOrders: 45 },
  { id: '4', name: 'BuildMat Solutions', email: 'orders@buildmat.com', phone: '+1-555-0104', status: 'active', rating: 4.6, totalOrders: 156 },
  { id: '5', name: 'FoodWholesale Co', email: 'contact@foodwholesale.com', phone: '+1-555-0105', status: 'inactive', rating: 3.9, totalOrders: 23 },
];

export const mockWarehouses = [
  { id: '1', name: 'Central Distribution Center', location: 'New York, NY', capacity: 50000, currentStock: 35000, status: 'operational' },
  { id: '2', name: 'West Coast Hub', location: 'Los Angeles, CA', capacity: 45000, currentStock: 42000, status: 'operational' },
  { id: '3', name: 'Southern Regional', location: 'Houston, TX', capacity: 30000, currentStock: 18000, status: 'operational' },
  { id: '4', name: 'Midwest Facility', location: 'Chicago, IL', capacity: 40000, currentStock: 28000, status: 'maintenance' },
  { id: '5', name: 'Northwest Storage', location: 'Seattle, WA', capacity: 25000, currentStock: 15000, status: 'operational' },
];

export const mockProducts = [
  { id: '1', sku: 'ELEC-001', name: 'Wireless Mouse', category: 'Electronics', price: 29.99, stock: 450, warehouseId: '1', reorderLevel: 100, vendor: 'Global Electronics Corp' },
  { id: '2', sku: 'ELEC-002', name: 'USB-C Cable', category: 'Electronics', price: 12.99, stock: 820, warehouseId: '1', reorderLevel: 200, vendor: 'TechSupply Industries' },
  { id: '3', sku: 'AUTO-001', name: 'Oil Filter', category: 'Auto Parts', price: 8.50, stock: 340, warehouseId: '2', reorderLevel: 150, vendor: 'AutoParts International' },
  { id: '4', sku: 'BUILD-001', name: 'Hammer', category: 'Tools', price: 24.99, stock: 180, warehouseId: '3', reorderLevel: 50, vendor: 'BuildMat Solutions' },
  { id: '5', sku: 'ELEC-003', name: 'Keyboard', category: 'Electronics', price: 49.99, stock: 280, warehouseId: '1', reorderLevel: 75, vendor: 'Global Electronics Corp' },
  { id: '6', sku: 'FOOD-001', name: 'Coffee Beans (5kg)', category: 'Food', price: 45.00, stock: 95, warehouseId: '4', reorderLevel: 100, vendor: 'FoodWholesale Co' },
];

export const mockOrders = [
  { id: '1', orderNumber: 'PO-2024-001', vendor: 'Global Electronics Corp', items: 3, total: 1450.50, status: 'delivered', date: '2024-05-15', expectedDelivery: '2024-05-20' },
  { id: '2', orderNumber: 'PO-2024-002', vendor: 'TechSupply Industries', items: 5, total: 2340.00, status: 'in_transit', date: '2024-05-18', expectedDelivery: '2024-05-25' },
  { id: '3', orderNumber: 'PO-2024-003', vendor: 'BuildMat Solutions', items: 2, total: 890.75, status: 'pending', date: '2024-05-20', expectedDelivery: '2024-05-27' },
  { id: '4', orderNumber: 'PO-2024-004', vendor: 'AutoParts International', items: 8, total: 3200.00, status: 'approved', date: '2024-05-22', expectedDelivery: '2024-05-29' },
];

export const mockShipments = [
  { id: '1', trackingNumber: 'TRK-001234567', orderId: '1', origin: 'New York, NY', destination: 'Boston, MA', status: 'delivered', carrier: 'FedEx', estimatedDelivery: '2024-05-20', actualDelivery: '2024-05-19' },
  { id: '2', trackingNumber: 'TRK-001234568', orderId: '2', origin: 'Los Angeles, CA', destination: 'Seattle, WA', status: 'in_transit', carrier: 'UPS', estimatedDelivery: '2024-05-25', actualDelivery: null },
  { id: '3', trackingNumber: 'TRK-001234569', orderId: '4', origin: 'Houston, TX', destination: 'Miami, FL', status: 'processing', carrier: 'DHL', estimatedDelivery: '2024-05-29', actualDelivery: null },
];

export const mockInvoices = [
  { id: '1', invoiceNumber: 'INV-2024-001', orderId: '1', vendor: 'Global Electronics Corp', amount: 1450.50, status: 'paid', issueDate: '2024-05-15', dueDate: '2024-06-15', paidDate: '2024-05-18' },
  { id: '2', invoiceNumber: 'INV-2024-002', orderId: '2', vendor: 'TechSupply Industries', amount: 2340.00, status: 'pending', issueDate: '2024-05-18', dueDate: '2024-06-18', paidDate: null },
  { id: '3', invoiceNumber: 'INV-2024-003', orderId: '3', vendor: 'BuildMat Solutions', amount: 890.75, status: 'overdue', issueDate: '2024-04-20', dueDate: '2024-05-20', paidDate: null },
];

export const mockUsers = [
  { id: '1', name: 'John Admin', email: 'admin@scm.com', role: 'admin', status: 'active', lastLogin: '2024-05-24' },
  { id: '2', name: 'Sarah Manager', email: 'warehouse@scm.com', role: 'warehouse_manager', status: 'active', lastLogin: '2024-05-24' },
  { id: '3', name: 'Mike Vendor', email: 'vendor@scm.com', role: 'vendor', status: 'active', lastLogin: '2024-05-23' },
  { id: '4', name: 'Lisa Driver', email: 'delivery@scm.com', role: 'delivery_personnel', status: 'active', lastLogin: '2024-05-24' },
];

export const mockDashboardStats = {
  totalRevenue: 125340.50,
  totalOrders: 248,
  activeShipments: 34,
  lowStockItems: 12,
  revenueChange: 12.5,
  ordersChange: 8.3,
  shipmentsChange: -3.2,
  stockChange: -15.4,
};

export const mockRevenueData = [
  { month: 'Jan', revenue: 45000 },
  { month: 'Feb', revenue: 52000 },
  { month: 'Mar', revenue: 48000 },
  { month: 'Apr', revenue: 61000 },
  { month: 'May', revenue: 55000 },
  { month: 'Jun', revenue: 68000 },
];

export const mockOrderStatusData = [
  { name: 'Pending', value: 35 },
  { name: 'Approved', value: 45 },
  { name: 'In Transit', value: 58 },
  { name: 'Delivered', value: 110 },
];

export const mockInventoryByCategory = [
  { category: 'Electronics', count: 1550 },
  { category: 'Auto Parts', count: 890 },
  { category: 'Tools', count: 450 },
  { category: 'Food', confidence: 320 },
];
