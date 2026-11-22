# 🐾 PetPal - Pet Adoption Tracker

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00.svg?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3-38B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

PetPal is a modern, lightweight, and container-ready full-stack web application designed for DevOps demonstration, CI/CD pipelines, container orchestration, and Kubernetes deployments.

It pairs a clean, pastel-themed UI with an enterprise-grade backend architecture, database resilience, and a dedicated database-backed `/health` probe.

---

## 🏗️ Architecture & Tech Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python ASGI Framework)
- **Database ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Database Drivers:**
  - **MySQL:** `PyMySQL` + `cryptography` (configured via `DATABASE_URL`)
  - **SQLite:** Built-in zero-configuration fallback (`sqlite:///./petpal.db`)
- **Frontend:** Server-rendered HTML with Jinja2 templates, styled using **Tailwind CSS** (via CDN) with vanilla JavaScript.
- **Containerization:** Non-root, slim Debian Docker container with automated `HEALTHCHECK`.
- **Testing:** `pytest` + FastAPI `TestClient` (`httpx`).

---

## 📁 Project Structure

```text
├── Dockerfile              # Multi-stage/slim container build with non-root user & HEALTHCHECK
├── docker-compose.yml      # Orchestration for FastAPI app + MySQL 8 container
├── .dockerignore           # Prevents bloated images by excluding local caches & DBs
├── .gitignore              # Clean Python & environment ignore definitions
├── main.py                 # FastAPI application, routes, lifespan & DB session handling
├── models.py               # SQLAlchemy models (Pet entity & species-aware helper methods)
├── requirements.txt        # Pinned Python package dependencies
├── test_main.py            # Automated pytest suite testing /health and page rendering
├── templates/
│   └── index.html          # Responsive pastel Tailwind UI with live DevOps health monitor
└── README.md               # Complete setup, running, and DevOps guide
```

---

## ⚡ Quick Start: Local Development (SQLite Fallback)

By default, PetPal starts with an embedded SQLite database if no `DATABASE_URL` is provided. This allows immediate zero-configuration local runs.

### 1. Clone & Setup Virtual Environment

```bash
# Navigate to the project directory
cd "Devops project"

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open your browser and navigate to:
- **Application UI:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **DevOps Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🐬 Running with MySQL

PetPal uses an environment variable named `DATABASE_URL`.

### Database Connection Format:
```text
mysql+pymysql://<username>:<password>@<host>:<port>/<database_name>
```

For your local credentials (`username: root`, `password: root`):

### Windows (PowerShell):
```powershell
$env:DATABASE_URL="mysql+pymysql://root:root@localhost:3306/petpal"
uvicorn main:app --reload --port 8000
```

### Linux / macOS (Bash):
```bash
export DATABASE_URL="mysql+pymysql://root:root@localhost:3306/petpal"
uvicorn main:app --reload --port 8000
```

> **Note:** Ensure a database named `petpal` exists in your MySQL server (`CREATE DATABASE IF NOT EXISTS petpal;`). SQLAlchemy will automatically generate the `pets` table and seed demo entries upon startup.

---

## 🐳 Running with Docker

### 1. Build the Docker Image
```bash
docker build -t petpal:latest .
```

The Dockerfile implements key DevOps best practices:
- Uses `python:3.11-slim` for minimal image size.
- Runs under an unprivileged user (`appuser`, UID 1000).
- Installs `curl` for container health monitoring.
- Includes a native `HEALTHCHECK` probing `GET /health`.

### 2. Run the Container (Standalone with SQLite)
```bash
docker run -d --name petpal-app -p 8000:8000 petpal:latest
```

### 3. Inspect Container Health
```bash
docker inspect --format='{{json .State.Health.Status}}' petpal-app
# Output: "healthy"
```

---

## 🚀 Running with Docker Compose (Full Stack: App + MySQL)

Spin up both MySQL 8 and the FastAPI application connected via an internal bridge network with automated health dependencies:

```bash
docker compose up -d --build
```

- **FastAPI Web App:** [http://localhost:8000](http://localhost:8000)
- **MySQL Database Port:** `3306` (Root Password: `root`, DB: `petpal`)

To shut down:
```bash
docker compose down
```

---

## 🧪 Running Automated Tests

The project includes unit and integration tests using `pytest` and FastAPI's `TestClient`.

Run the test suite:
```bash
pytest test_main.py -v
```

### What the test suite covers:
1. **`test_health_check`**: Probes `GET /health`, verifying HTTP 200 OK and `{"status": "healthy", "database": "connected"}`.
2. **`test_main_page_loads`**: Probes `GET /`, confirming HTTP 200 OK and valid HTML template rendering with PetPal branding.
3. **`test_add_pet`**: Validates submitting a pet via `POST /pets` and confirms redirection (`HTTP 303`).
4. **`test_adopt_pet`**: Validates marking a pet as adopted via `POST /pets/{id}/adopt`.

---

## 🩺 DevOps Health Check Endpoint (`GET /health`)

The `/health` endpoint is instrumented for Kubernetes liveness/readiness probes, Docker healthchecks, and load balancer pingers.

### Active DB Verification
Instead of a simple static string, `/health` runs a lightweight database ping:
```sql
SELECT 1;
```

#### Healthy Response (`HTTP 200 OK`):
```json
{
  "status": "healthy",
  "database": "connected"
}
```

#### Degraded / Disconnected Response (`HTTP 503 Service Unavailable`):
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "..."
}
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Renders the PetPal web interface (Jinja2 template) |
| `POST` | `/pets` | Form submission to create a new pet companion |
| `POST` | `/pets/{id}/adopt` | Updates pet status to **Adopted** |
| `GET` | `/health` | DevOps health check probing DB connectivity with `SELECT 1` |
| `GET` | `/docs` | Interactive OpenAPI Swagger UI documentation |
