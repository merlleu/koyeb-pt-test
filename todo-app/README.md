# Todo App

A complete todo application with a FastAPI backend, single-page frontend, and full test coverage (pytest unit tests + Playwright e2e tests).

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** Vanilla HTML/CSS/JS SPA (no build step)
- **Tests:** pytest (API) + Playwright (e2e)
- **Package manager:** uv

## Features

- Create, read, update, delete (CRUD) todos
- Title, description, priority (low/medium/high)
- Toggle complete/incomplete
- Filter by status (all/active/completed) and priority
- Search by title or description
- Sort by created date, priority, or title
- Stats dashboard (total, active, completed, high-priority)
- Clear all completed todos
- Toast notifications
- Persistent storage via SQLite
- Fully responsive UI

## Setup

```bash
cd todo-app
uv sync                    # install dependencies
uv run playwright install chromium   # install browser for e2e tests
```

## Run the app

```bash
uv run uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000

## Run tests

```bash
# API unit tests
uv run pytest tests/test_api.py

# E2e tests (requires a running browser)
uv run pytest tests/e2e/

# All tests
uv run pytest
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/todos` | List todos (supports `completed`, `priority`, `search`, `sort` query params) |
| `GET` | `/api/todos/stats` | Get summary statistics |
| `POST` | `/api/todos` | Create a todo |
| `GET` | `/api/todos/{id}` | Get a single todo |
| `PATCH` | `/api/todos/{id}` | Update a todo |
| `POST` | `/api/todos/{id}/toggle` | Toggle completion status |
| `DELETE` | `/api/todos/{id}` | Delete a todo |
| `DELETE` | `/api/todos` | Clear all completed todos |

## Project Structure

```
todo-app/
├── app/
│   ├── main.py          # FastAPI app entrypoint
│   ├── config.py        # Configuration
│   ├── database.py      # SQLAlchemy engine & sessions
│   ├── models.py        # DB models
│   ├── schemas.py       # Pydantic validation schemas
│   ├── crud.py          # CRUD operations
│   ├── routes.py        # API routes
│   └── static/
│       └── index.html    # Frontend SPA
├── tests/
│   ├── conftest.py      # API test fixtures
│   ├── test_api.py      # API unit tests
│   └── e2e/
│       ├── conftest.py  # Playwright fixtures & server
│       └── test_todo_app.py  # E2e UI tests
├── pyproject.toml
└── README.md
```
