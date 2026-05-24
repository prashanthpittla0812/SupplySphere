# SupplySphere — Enterprise Supply Chain Management System

A full-stack enterprise application for supply chain management with role-based dashboards, real-time tracking, and analytics.

## Project Structure

```
SupplySphere/
├── frontend/          # React + Vite + Tailwind CSS + TypeScript
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/   # shadcn/ui + custom components
│   │   │   ├── pages/        # 11 route pages with real API integration
│   │   │   ├── services/     # Axios API layer with refresh token rotation
│   │   │   ├── store/        # Zustand auth store
│   │   │   └── routes.tsx    # Protected route definitions
│   │   └── styles/
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
│
├── backend/           # Node.js + Express + TypeScript + Prisma
│   ├── src/
│   │   ├── config/           # Env, database, redis, swagger
│   │   ├── middleware/        # Auth, RBAC, validation, error handler
│   │   ├── modules/          # 11 business modules
│   │   ├── sockets/          # Socket.io real-time engine
│   │   ├── jobs/             # BullMQ background workers
│   │   └── tests/            # Jest + Supertest
│   ├── prisma/
│   │   ├── schema.prisma     # 15 tables with relations
│   │   └── seed.ts           # Seed data with 4 role-based users
│   ├── docker-compose.yml    # Backend + Postgres + Redis + Nginx
│   └── package.json
│
└── README.md
```

## Tech Stack

### Frontend
- React 18 + TypeScript
- Vite 6 + Tailwind CSS 4
- Zustand (state management)
- Axios (API client with interceptors)
- Recharts (analytics dashboards)
- shadcn/ui + Radix UI primitives
- React Router v7 (protected routes)

### Backend
- Node.js + Express + TypeScript
- PostgreSQL + Prisma ORM
- JWT authentication with refresh token rotation
- Zod validation
- Socket.io (real-time)
- BullMQ + Redis (background jobs)
- Swagger/OpenAPI docs
- Pino logging
- Jest + Supertest testing
- Docker + Docker Compose

## Quick Start

### Prerequisites
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

### Backend Setup

```bash
cd backend
cp .env.example .env   # Edit database credentials
npm install
npx prisma generate
npx prisma db push
npx prisma db seed
npm run dev             # Starts on :5000
```

### Frontend Setup

```bash
cd frontend
npm install
npx vite               # Starts on :5173
```

Open http://localhost:5173

### Seed Users

| Email | Password | Role |
|-------|----------|------|
| admin@scm.com | Admin@123 | Admin |
| warehouse@scm.com | Warehouse@123 | Warehouse Manager |
| vendor@scm.com | Vendor@123 | Vendor |
| delivery@scm.com | Delivery@123 | Delivery Personnel |

### Docker Deployment

```bash
cd backend
docker-compose up --build -d
```

## Architecture Highlights

- **Clean Architecture**: Controllers → Services → Repositories → ORM
- **Role-Based Access**: Admin, Warehouse Manager, Vendor, Delivery Personnel
- **Real-Time Updates**: Socket.io for shipments, inventory alerts, notifications
- **Background Processing**: BullMQ queues for emails, invoices, reports
- **API Documentation**: Swagger UI at `/api/docs`
- **Security**: Helmet, CORS, rate limiting, JWT rotation, input sanitization
- **Scalability**: Modular monolith designed for microservices extraction
