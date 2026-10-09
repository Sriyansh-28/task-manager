# Task Manager

A small full-stack task manager: a React + Material UI frontend, a Flask REST API, and MongoDB for storage. Includes pytest tests, a GitHub Actions CI workflow, Docker, and a Bash test script.

## Features

- List, add, complete and delete tasks
- Tasks persisted in MongoDB
- Input validation and JSON error responses with proper HTTP status codes
- Loading states and error messages in a responsive UI

## Project structure

```
backend/app.py                 Flask API
backend/test_app.py            pytest tests (mongomock, no database needed)
backend/requirements.txt       runtime dependencies (pinned)
backend/requirements-dev.txt   runtime + test dependencies (pinned)
frontend/                      React + Material UI app (Vite)
scripts/test.sh                runs the backend tests
backend/wsgi.py                entrypoint for Vercel
Dockerfile                     backend image
vercel.json                    Vercel deployment (frontend + backend)
docker-compose.yml             backend + MongoDB
.github/workflows/ci.yml       CI: tests + Docker build
```

## API

| Method | Path                   | Body                    | Success |
| ------ | ---------------------- | ----------------------- | ------- |
| GET    | `/health`              | –                       | 200     |
| GET    | `/api/tasks`           | –                       | 200     |
| POST   | `/api/tasks`           | `{"title": "Buy milk"}` | 201     |
| PATCH  | `/api/tasks/<task_id>` | `{"completed": true}`   | 200     |
| DELETE | `/api/tasks/<task_id>` | –                       | 204     |

Errors are returned as `{"error": "..."}` with 400 (invalid input or id), 404 (task not found) or 503 (database unavailable).

## Prerequisites

- Python 3.11+
- Node.js 20.19+ or 22.12+
- Docker Desktop (for MongoDB and the containerized backend)

## Run the application

### 1. Backend + MongoDB (Docker)

```bash
docker compose up --build -d
curl http://127.0.0.1:5000/health
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The dev server proxies `/api` to the backend on port 5000.

### Alternative: backend without Docker

Requires a MongoDB server (local or Atlas). Configuration is read from environment variables; see `.env.example`.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
export MONGO_URI="mongodb://localhost:27017"   # PowerShell: $env:MONGO_URI = "..."
python app.py
```

## Run the tests

```bash
./scripts/test.sh --install    # first run: installs dependencies, then tests
./scripts/test.sh              # later runs
```

On Windows without Git Bash: `cd backend` then `python -m pytest -v`.

## Configuration

| Variable           | Default                     | Used by             |
| ------------------ | --------------------------- | ------------------- |
| `MONGO_URI`        | `mongodb://localhost:27017` | backend             |
| `MONGO_DB_NAME`    | `taskmanager`               | backend             |
| `FLASK_HOST`       | `127.0.0.1`                 | `python app.py`     |
| `PORT`             | `5000`                      | `python app.py`     |
| `API_PROXY_TARGET` | `http://127.0.0.1:5000`     | frontend dev server |

Never commit real credentials. `.env` is git-ignored; `.env.example` holds placeholders only.

## Deploy (Vercel + MongoDB Atlas)

`vercel.json` deploys both parts as one Vercel project: the React app as a static
frontend and the Flask API as a serverless function (`backend/wsgi.py`), on the same
domain. The database is a MongoDB Atlas cluster.

1. Create a free Atlas cluster and a database user, and allow access from anywhere
   (`0.0.0.0/0`) because Vercel functions have no fixed IP address.
2. Import the GitHub repository in Vercel, keeping the repository root as the root directory.
3. Add the environment variables `MONGO_URI` (the Atlas connection string) and
   `MONGO_DB_NAME` in the Vercel project settings, then deploy.

The connection string is a secret: set it only in Vercel, never in the repository.

## Stop

```bash
docker compose down        # add -v to also delete the stored tasks
```
