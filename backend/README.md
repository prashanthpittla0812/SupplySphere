# SupplySphere Backend

Production-oriented FastAPI backend for the SupplySphere enterprise supply chain management system.

## Stack

- FastAPI, Uvicorn, Pydantic
- PostgreSQL with SQLAlchemy 2 async ORM
- JWT access tokens, refresh tokens, bcrypt password hashing
- Redis, Celery workers, Celery beat
- FastAPI WebSockets for live shipment, inventory, dashboard, and notification events
- Alembic migrations
- Pytest API and service tests
- Docker Compose with FastAPI, PostgreSQL, Redis, Celery, and Nginx

FastAPI default API docs are available at `http://localhost:5000/api/docs` in local development.

## Project Layout

```text
backend/
  app/
    api/v1/          REST routers
    core/            config, security, database, dependencies, exceptions
    models/          SQLAlchemy ORM models
    schemas/         Pydantic request/response schemas
    services/        business workflows
    repositories/    data access
    middleware/      rate limiting
    tasks/           Celery jobs
    utils/           pagination, PDFs, file storage
    ws/              WebSocket connection manager
    main.py          FastAPI app entrypoint
  alembic/           migrations
  docker/            Nginx config
  tests/             pytest test suite
```

## Local Development Without Docker

```powershell
cd C:\Users\Prashanth\Downloads\SupplySphere\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python seed.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

The frontend is configured to call `/api`, so run Vite on `http://localhost:5173` and the backend on port `5000` or proxy through Nginx.

## Docker Deployment

Docker Desktop must be installed and running.

```powershell
cd C:\Users\Prashanth\Downloads\SupplySphere\backend
docker compose up --build
```

Services:

- `backend`: FastAPI app on `8000` inside Docker
- `postgres`: PostgreSQL 16
- `redis`: Redis 7
- `celery-worker`: background jobs
- `celery-beat`: scheduled jobs
- `nginx`: public gateway on `http://localhost`

## API Groups

- `/api/auth`
- `/api/users`
- `/api/vendors`
- `/api/products`
- `/api/inventory`
- `/api/warehouses`
- `/api/orders`
- `/api/shipments`
- `/api/invoices`
- `/api/notifications`
- `/api/analytics`
- `/api/audit-logs`
- `/api/uploads`

## Authentication Flow

Login returns both frontend-friendly and backend-friendly token fields:

```json
{
  "success": true,
  "data": {
    "user": { "id": "...", "email": "admin@supplysphere.com", "name": "Admin", "role": "admin" },
    "tokens": { "accessToken": "...", "refreshToken": "..." },
    "access_token": "...",
    "refresh_token": "..."
  }
}
```

Use `Authorization: Bearer <accessToken>` for protected APIs and call `/api/auth/refresh-token` with `{ "refreshToken": "..." }`.

## WebSockets

Connect with a JWT access token:

```text
ws://localhost:5000/ws?token=<accessToken>
```

The connection manager supports role and user scoped broadcasts for shipment tracking, inventory alerts, notifications, and dashboard live updates.

## Background Jobs

Celery modules live in `app/tasks`:

- email notifications
- invoice jobs
- notification dispatch
- scheduled low-stock/report workflows

Run manually:

```powershell
celery -A app.tasks.celery_app worker --loglevel=info
celery -A app.tasks.celery_app beat --loglevel=info
```

## Testing

```powershell
pytest -q
```

The test suite uses an isolated SQLite database via `aiosqlite` for fast API/integration tests.

## Production Notes

- Replace `SECRET_KEY` with a long random value.
- Use PostgreSQL in production: `postgresql://user:password@host:5432/db`.
- Keep `DEBUG=false`.
- Restrict `CORS_ORIGINS` to deployed frontend domains.
- Put Nginx or a cloud load balancer in front of Uvicorn workers.
- Store uploads on S3 by setting `STORAGE_TYPE=s3` and AWS credentials.
- Run `alembic upgrade head` during release startup before serving traffic.
