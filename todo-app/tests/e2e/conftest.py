"""Shared fixtures for Playwright e2e tests."""
import os
import socket
import threading
import time

import pytest
from playwright.sync_api import Page, sync_playwright


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _wait_for(port: int, timeout: float = 10.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.socket() as s:
                s.settimeout(0.5)
                s.connect(("127.0.0.1", port))
            return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError(f"Server on port {port} did not start")


@pytest.fixture(scope="session")
def server():
    """Start a uvicorn server for the e2e session and yield its base URL."""
    import uvicorn

    port = _free_port()
    # Ensure a fresh DB file for the e2e session (not in-memory, since uvicorn
    # runs in its own thread and needs a shared file).
    db_file = os.path.join(
        os.path.dirname(__file__), "..", "..", "e2e_test.db"
    )
    db_path = os.path.abspath(db_file)
    if os.path.exists(db_path):
        os.remove(db_path)
    os.environ["TODO_DB_PATH"] = db_path
    os.environ.pop("TODO_DATABASE_URL", None)
    os.environ["TODO_ENV"] = "dev"

    config = uvicorn.Config(
        "app.main:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    _wait_for(port)

    # Reset DB state before each session.
    from app.database import init_db
    init_db()

    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    thread.join(timeout=5)
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture()
def base_url(server: str) -> str:
    """Return base URL and clear all todos before each test."""
    import urllib.request

    # Delete all existing todos by fetching and deleting each one.
    req = urllib.request.Request(f"{server}/api/todos", method="DELETE")
    urllib.request.urlopen(req)
    yield server


@pytest.fixture()
def page(base_url: str):
    """Provide a Playwright page pointed at the running server."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(base_url)
        yield page
        context.close()
        browser.close()
