"""API layer: the mentoria app driven through FastAPI's TestClient.

Exactly two boundaries are replaced. Everything between the HTTP request and
the response (routing, guards, queries) is the real application code.

  - get_current_user: the real one calls the auth-service over HTTP (token
    introspection). Here the `login_as` fixture decides who is logged in.
  - get_session: SQLite in memory instead of Postgres. TEMPORARY deviation
    from ADR-Q14: Docker is not available in WSL yet. Swap the `engine`
    fixture for the compose Postgres when it is.
"""
import os

# app.database builds its engine at import time from DATABASE_URL, and an
# empty URL crashes the import. That engine is never used (get_session is
# overridden below), but the URL has to be parseable.
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from app.auth_dependency import get_current_user  # noqa: E402
from app.database import get_session  # noqa: E402
# main.py mounts StaticFiles(directory="front"), a path relative to the
# working directory, checked at import time. In production the app always
# starts from its own folder, so import it from there and come straight back.
_cwd = os.getcwd()
os.chdir(os.environ["MENTORIA_SRC"])
try:
    from app.main import app  # noqa: E402
finally:
    os.chdir(_cwd)
from app.models import Mentorando  # noqa: E402

# Same rule as tests/unit/conftest.py: non-null columns nobody here cares about.
# Duplicated on purpose for now; shared fixtures are S10.
REQUIRED_FIELD_DEFAULTS = {"nivel_formacao": "Mestrado"}


@pytest.fixture
def engine():
    """Fresh in-memory schema per test, shared across threads."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(eng)
    yield eng
    SQLModel.metadata.drop_all(eng)


@pytest.fixture
def session(engine):
    with Session(engine) as sess:
        yield sess


@pytest.fixture
def client(session):
    """TestClient wired to the test database. Clears every override on teardown."""
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def login_as(client):
    """Replace the auth-service: whoever is passed here is the logged-in user."""

    def _login(email: str, level: str = "Editar", is_admin: bool = False) -> dict:
        user = {"email": email, "level": level, "is_admin": is_admin}
        app.dependency_overrides[get_current_user] = lambda: user
        return user

    return _login


@pytest.fixture
def make_mentorando(session):
    """Insert a Mentorando and return it."""

    def _make(email: str, nome: str = "Test Subject", **extra) -> Mentorando:
        fields = {**REQUIRED_FIELD_DEFAULTS, "email": email, "nome": nome, **extra}
        item = Mentorando(**fields)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    return _make