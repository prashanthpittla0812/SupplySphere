You are a Senior Full Stack Software Engineer and Enterprise Solution Architect.

Build a production-level enterprise application called:

“Supply Chain Management System”

The application should follow real-world enterprise architecture, SDLC practices, scalable backend design, clean UI/UX principles, authentication, API documentation, testing structure, and modern DevOps-ready practices.

==========================================================
PROJECT OVERVIEW
==========================================================

The Supply Chain Management System should manage:

1. Vendors
2. Warehouses
3. Inventory
4. Purchase Orders
5. Shipment Tracking
6. Billing & Invoices
7. Role-Based Users
8. Analytics Dashboard

The application must support multiple user roles:
- Admin
- Warehouse Manager
- Vendor
- Delivery Personnel

==========================================================
TECH STACK
==========================================================

FRONTEND:
- React.js
- Vite
- Tailwind CSS
- Shadcn UI
- React Router DOM
- Axios
- React Hook Form
- Zustand or Redux Toolkit
- Recharts or Chart.js

BACKEND:
- Node.js
- Express.js

DATABASE:
- PostgreSQL

AUTHENTICATION:
- JWT Authentication
- Refresh Tokens
- Role-Based Access Control (RBAC)

API DOCUMENTATION:
- Swagger / OpenAPI

TESTING:
- Jest
- Supertest

DEVOPS:
- Docker support
- Environment variables
- CI/CD ready structure

==========================================================
ARCHITECTURE REQUIREMENTS
==========================================================

Build the application initially using MONOLITHIC ARCHITECTURE.

Backend modules should be separated cleanly into:
- auth
- users
- vendors
- inventory
- warehouses
- shipments
- billing
- analytics

Structure the backend so it can later be converted into MICROSERVICES.

Use:
- Controllers
- Services
- Repositories
- Middleware
- DTO validation
- Utility layer
- Config layer

==========================================================
FRONTEND REQUIREMENTS
==========================================================

Create a professional enterprise UI dashboard.

Features:
- Responsive layout
- Sidebar navigation
- Header/navbar
- Dark/light mode
- Analytics dashboard
- Protected routes
- Role-based UI rendering
- Toast notifications
- Loading states
- Error boundaries

Pages Required:
- Login
- Register
- Forgot Password
- Dashboard
- Vendors
- Inventory
- Warehouses
- Shipments
- Billing
- Reports
- User Management
- Settings

==========================================================
BACKEND REQUIREMENTS
==========================================================

Build REST APIs for all modules.

Use:
- Express Router
- Middleware architecture
- JWT middleware
- Error handling middleware
- Request validation
- Logging

==========================================================
DATABASE DESIGN
==========================================================

Create PostgreSQL schema with relationships.

Required tables:
- users
- roles
- vendors
- warehouses
- products
- inventory
- purchase_orders
- purchase_order_items
- shipments
- invoices
- notifications
- audit_logs

Use:
- UUIDs
- Foreign keys
- Timestamps
- Soft delete support

==========================================================
AUTHENTICATION & SECURITY
==========================================================

Implement:
- JWT login
- Refresh tokens
- Password hashing with bcrypt
- Role-based authorization
- API rate limiting
- Helmet security
- CORS
- Input sanitization
- SQL injection prevention

==========================================================
FEATURE REQUIREMENTS
==========================================================

1. AUTH MODULE
- Register users
- Login
- Logout
- Refresh token
- Forgot password
- Reset password

2. USER MANAGEMENT
- Create users
- Assign roles
- Activate/deactivate users

3. VENDOR MANAGEMENT
- Add vendors
- Update vendors
- Vendor approval workflow

4. INVENTORY MANAGEMENT
- Add products
- Update stock
- Low stock alerts
- Warehouse stock mapping

5. PURCHASE ORDERS
- Create purchase orders
- Approve/reject orders
- Order status tracking

6. SHIPMENT TRACKING
- Shipment status
- Delivery confirmation
- Tracking history

7. BILLING & INVOICES
- Generate invoices
- Payment tracking
- Download invoice PDF

8. ANALYTICS DASHBOARD
- Inventory analytics
- Shipment analytics
- Vendor performance
- Revenue charts

==========================================================
API REQUIREMENTS
==========================================================

Document all APIs using Swagger OpenAPI.

Example API groups:
- /api/auth
- /api/users
- /api/vendors
- /api/products
- /api/inventory
- /api/orders
- /api/shipments
- /api/invoices
- /api/analytics

Each API must include:
- Validation
- Error responses
- Status codes
- Swagger documentation

==========================================================
TESTING REQUIREMENTS
==========================================================

Implement:
- Unit tests
- Integration tests
- API tests

Use:
- Jest
- Supertest

==========================================================
DEVOPS REQUIREMENTS
==========================================================

Provide:
- Dockerfile
- docker-compose.yml
- .env.example
- Production-ready configuration

==========================================================
UI/UX REQUIREMENTS
==========================================================

Design should look modern enterprise-level:
- Professional dashboard
- Clean cards
- Data tables
- Filters
- Search
- Pagination
- Charts
- Responsive layouts

==========================================================
PROJECT STRUCTURE
==========================================================

FRONTEND:
src/
  components/
  pages/
  layouts/
  routes/
  services/
  hooks/
  store/
  utils/
  styles/

BACKEND:
src/
  config/
  modules/
  middleware/
  utils/
  database/
  docs/
  tests/

==========================================================
DELIVERABLES
==========================================================

Generate:
1. Full frontend code
2. Full backend code
3. PostgreSQL schema
4. API documentation
5. Swagger setup
6. Docker setup
7. Environment setup
8. Authentication flow
9. RBAC implementation
10. Professional README
11. Setup instructions
12. Sample seed data

==========================================================
CODING STANDARDS
==========================================================

Follow:
- Clean Architecture
- SOLID principles
- DRY principle
- Enterprise coding standards
- Scalable folder structure
- Proper naming conventions
- Reusable components
- Modular services

==========================================================
IMPORTANT
==========================================================

The project should look like a real enterprise product suitable for:
- CTO review
- Enterprise demos
- Resume projects
- Production-level portfolio

The code should be:
- Clean
- Modular
- Scalable
- Maintainable
- Well documented
- Professional

Generate the project step-by-step starting from:
1. Folder structure
2. Database schema
3. Backend setup
4. Frontend setup
5. Authentication
6. Modules one by one
7. Swagger documentation
8. Docker deployment
9. Final production optimization