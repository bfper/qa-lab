"""Root conftest — the safety gate for the whole lab.

Single responsibility: make it impossible for a test run to reach anything
that is not on this machine. If any configured endpoint resolves to a
non-local host, the session aborts before a single test is collected.

This runs at MODULE level, not in pytest_configure. pytest imports the
conftests along the path from rootdir down to the target directory, and only
then calls pytest_configure — so a guard living in the hook fires after
tests/unit/conftest.py has already imported the app. Module level is the
only place early enough.

This is deliberately blunt. A false positive costs you ten seconds of
editing .env. A false negative costs you production data.
"""
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import pytest

ROOT = Path(__file__).parent

# Hosts the lab is allowed to talk to. Nothing else, ever.
ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0", "host.docker.internal"}

# Environment variables that may carry a URL or a hostname.
GUARDED_VARS = (
    "BASE_URL",
    "AUTH_BASE_URL",
    "POSTGRES_HOST",
    "DATABASE_URL",
    "AUTH_DATABASE_URL",
)

# Substrings that must never appear in any guarded value.
FORBIDDEN_SUBSTRINGS = ("perazzo.cloud", "srv1797282")


def _abort(message: str) -> None:
    """Stop the run now. Raising beats pytest.exit() at module import time."""
    raise pytest.UsageError(f"\n\n{message}\n")


def _load_dotenv() -> None:
    """Minimal .env loader. Avoids a dependency for six lines of parsing."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def _extract_host(value: str) -> str:
    """Return the hostname from a URL, a host:port pair, or a bare host."""
    value = value.strip()
    if "://" in value:
        return (urlparse(value).hostname or "").lower()
    if "@" in value:
        value = value.rsplit("@", 1)[1]
    return value.split(":")[0].strip().lower()


def _assert_local(var: str, value: str) -> None:
    lowered = value.lower()
    for needle in FORBIDDEN_SUBSTRINGS:
        if needle in lowered:
            _abort(
                f"ABORTED: {var} contains '{needle}'.\n"
                f"  value: {value}\n"
                f"The lab must never point at production."
            )

    host = _extract_host(value)
    if host and host not in ALLOWED_HOSTS:
        _abort(
            f"ABORTED: {var} resolves to a non-local host '{host}'.\n"
            f"  value: {value}\n"
            f"Allowed: {', '.join(sorted(ALLOWED_HOSTS))}\n"
            f"Fix .env before running again."
        )


def _add_app_source_to_path() -> None:
    """Make the cloned app importable without installing it."""
    for var in ("MENTORIA_SRC",):
        raw = os.environ.get(var)
        if not raw:
            continue
        if not Path(raw).is_absolute():
            _abort(
                f"ABORTED: {var} must be an absolute path, got '{raw}'.\n"
                f"Relative paths resolve differently for pytest and for "
                f"docker compose. Use /home/<user>/lab/src/... in .env"
            )
        path = Path(raw)
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))


# --- runs at import, before any other conftest ------------------------------
_load_dotenv()

for _var in GUARDED_VARS:
    _value = os.environ.get(_var)
    if _value:
        _assert_local(_var, _value)

_add_app_source_to_path()


def pytest_report_header(config: pytest.Config) -> list[str]:
    src = os.environ.get("MENTORIA_SRC", "<unset>")
    return [
        f"qa-lab: host guard OK (allowed: {', '.join(sorted(ALLOWED_HOSTS))})",
        f"qa-lab: BASE_URL={os.environ.get('BASE_URL', '<unset>')} "
        f"AUTH={os.environ.get('AUTH_BASE_URL', '<unset>')}",
        f"qa-lab: MENTORIA_SRC={src}",
    ]
