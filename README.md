# 🚀 FastAPI Math Microservice – Cloud Version (GCP)

A scalable, production-ready microservice built with **FastAPI**, deployed on **Google Cloud Run**, enhanced with **Redis Memorystore** for caching and **Google Pub/Sub** for message streaming.

The application runs at: https://pycalc-fastapi-1042924434321.europe-central2.run.app/docs

This version includes **all base, optional, and bonus** requirements of the project, re-architected for a cloud-native, serverless environment.

This project has also a local-version branch in which the application is built with **Kafka** and **Redis** for local development and testing.

---

## ✅ Features

* 🧲 Endpoints for `fibonacci`, `factorial`, and `power`
* 🔐 JWT authentication with `bcrypt` password hashing
* 👥 Role-based access control (`user` and `admin`)
* 📎 Operation history stored in SQLite
* ⚡ Redis Memorystore caching (GCP-managed Redis)
* ↻ Google Pub/Sub for operation event streaming (instead of Kafka)
* 📊 Prometheus metrics at `/metrics`
* 🧪 Full testing suite with `pytest`
* 🧹 Code linted with `flake8`
* ⚙️ Asynchronous endpoints (`async def`)
* 📆 Packaged as Docker container and deployed to **Cloud Run**

---

## Project Structure

```
pycalc/
├── main.py                 # App entry + lifespan + metrics
├── routers/                # API routes: auth + math ops
├── services/               # MathService logic
├── db/                     # SQLite integration
├── models/                 # Pydantic schemas
├── cache/                  # Redis (Memorystore) client
├── streaming/              # Pub/Sub producer & consumer
├── requirements.txt        # Dependencies
├── Dockerfile              # For Cloud Run
├── .gcloudignore           # Excludes unnecessary files
└── README.md               # You're here
```

---

## ☁️ Google Cloud Components

* **Cloud Run** – Deploys the FastAPI app serverlessly
* **Pub/Sub** – Streams operation metadata (instead of Kafka)
* **Memorystore** – Redis-managed caching layer
* **Cloud Build** – Builds the container image on deploy
* **VPC Connector** – Enables access to Memorystore from Cloud Run

---

## 🚀 Deployment (Cloud Run)

1. **Enable APIs**:
   Cloud Run, Cloud Build, Pub/Sub, Redis, VPC Access

2. **Create Redis (Memorystore)**:

3. **Create Pub/Sub Topic + Subscription**:

4. **Create VPC Connector**:

5. **Deploy to Cloud Run**:

---

## 🔐 Authentication Flow

1. `POST /register` → create user (with role: `user` or `admin`)
2. `POST /login` → returns `access_token`
3. Add token in headers:
   `Authorization: Bearer <access_token>`
4. Access secured endpoints:

   * `/fibonacci/{n}`
   * `/factorial/{n}`
   * `/pow/{x}/{y}`
   * `/secure-history`

---

## 📊 Monitoring

* Prometheus metrics available at `/metrics`
* Includes route counters, status code metrics, response times

---

## 🧪 Testing

Run with:

```bash
pytest -v -s
```

Test coverage:

* Register + login flow
* Authenticated math operations
* Role-based access to `/secure-history`
* Caching via Redis
* Streaming via Pub/Sub
* Token invalidation
* Edge cases

---

## 🧹 Linting

```bash
flake8 .
```

## 🧠 Notes

* Built with Python 3.13 + FastAPI
* Structured using MVCS (Models, Views, Controllers, Services)
* Fully async and production-ready
* Easily extendable (e.g., token blacklist, CI/CD, frontend)
* ✅ Cloud-native stack (Cloud Run, Pub/Sub, Redis)

---

## 🛡️ Branches

| Branch          | Description                            |
| --------------- | -------------------------------------- |
| `local-version` | Local development with Kafka & Redis   |
| `cloud-version` | Deployed on GCP: Pub/Sub + Memorystore |

---

## 📌 Links

* Live Swagger Docs: `https://pycalc-fastapi-1042924434321.europe-central2.run.app/docs`
* Prometheus metrics: `https://pycalc-fastapi-1042924434321.europe-central2.run.app/metrics`

---
