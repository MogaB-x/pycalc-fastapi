# FastAPI Math Microservice

A production-ready microservice built with **FastAPI** that provides mathematical operations over a secured API. The service includes user registration, JWT-based authentication, role-based access control, request caching with Redis, and per-user operation history stored in a **SQLite** database.

## Features

* REST API with fibonacci, factorial, and power operations
* Asynchronous endpoints using async def
* SQLite persistence of all API requests
* In-memory and Redis-based caching to prevent recalculations
* User registration with **bcrypt** password hashing
* JWT authentication via python-jose
* Role system: user (personal history), admin (full history)
* Protected endpoints with Bearer <token> authorization
* Test suite with pytest and httpx.AsyncClient
* Prometheus integration at /metrics for monitoring
* Docker support via Dockerfile and docker-compose
* Linted with flake8 and structured using MVCS best practices

## Project Structure

```
pycalc/
├── main.py                   # FastAPI app with lifespan + Prometheus
├── routers/                  # math_router.py, auth_router.py
├── services/                 # MathService with OOP logic
├── db/                       # SQLite connection and operations
├── models/                   # Pydantic models (input/output validation)
├── cache/                    # Redis cache integration
├── tests/                    # Automated tests with JWT flow
├── requirements.txt          # Installed dependencies
├── Dockerfile                # Docker image for the app
├── docker-compose.yml        # Runs app + Redis together
└── README.md
```

## How to Run

### Local (venv)

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### With Docker Compose

```bash
docker compose up --build
```

Access app at: [http://localhost:8000/docs](http://localhost:8000/docs)

## API Authentication Flow

1. `POST /register` – Create user (role = user or admin)
2. `POST /login` – Receive `access_token`
3. Use token in:

   ```
   Authorization: Bearer <access_token>
   ```
4. Access protected endpoints:

   * `GET /fibonacci/{n}`
   * `GET /secure-history` (personal or all if admin)

## Running Tests

```bash
pytest -v -s
```

Tests include:

* Register + Login
* Operation calls with token
* Secure history per user
* Admin view of full history
* Token invalidation after user deletion
* Caching behavior (Redis)
* Role restrictions and validation

## Monitoring

* Prometheus metrics exposed at `GET /metrics`
* Includes total request count, per-route stats, and status codes

## Notes

* Built using Python 3.13
* Redis required for caching (run via docker-compose)
* Fully modular (MVCS): clean separation of logic, routes, DB, models
* Ready for extension: async workers, token blacklist, external frontend
