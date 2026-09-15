"""Week 1 — in-memory database, no container required.

check_scope() takes a live Session, so these are not pure unit tests in the
textbook sense. SQLite in memory keeps them fast (milliseconds) and keeps
week 1 free of Docker, which is the point.

If importing app.models blows up on a Postgres-only column type, stop
fighting it: move this layer onto the compose Postgres and carry on.
"""
import os

import pytest
from sqlmodel import Session, SQLModel, create_engine


def _require_app_source():
    """Import the app under test, or skip with an actionable message."""
    try:
        from app.models import Mentorando  # noqa: F401
        from app.scope import (  # noqa: F401
            check_acesso_compartilhavel,
            check_scope,
            get_proprio_mentorando,
            is_gerente,
            require_gerente,
        )
    except ImportError as exc:
        pytest.skip(
            f"app source not importable ({exc}). "
            f"Clone mentoria into MENTORIA_SRC (currently "
            f"{os.environ.get('MENTORIA_SRC', '<unset>')}) and remove its git remote.",
            allow_module_level=True,
        )


_require_app_source()

from app.models import Mentorando  # noqa: E402


@pytest.fixture
def engine():
    """Fresh schema per test. Isolation beats speed at this size."""
    eng = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(eng)
    yield eng
    SQLModel.metadata.drop_all(eng)


@pytest.fixture
def session(engine):
    with Session(engine) as sess:
        yield sess


@pytest.fixture
def make_mentorando(session):
    """Insert a Mentorando and return it.

    Keep the signature minimal: if app.models requires more non-null fields,
    add them here as defaults rather than in every test.
    """

    def _make(email: str, nome: str = "Test Subject", **extra) -> Mentorando:
        item = Mentorando(email=email, nome=nome, **extra)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    return _make


@pytest.fixture
def make_user():
    """Build the `user` dict that check_scope() receives.

    Mirrors what get_current_user returns. Kept as a plain dict on purpose:
    the production code reads it with .get(), so there is nothing to mock.
    """

    def _make(email: str = "", level: str = "Visualizar", is_admin: bool = False) -> dict:
        return {"email": email, "level": level, "is_admin": is_admin}

    return _make
