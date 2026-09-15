"""Root conftest — the safety gate for the whole lab.

Single responsibility: make it impossible for a test run to reach anything
that is not on this machine. If any configured endpoint resolves to a
non-local host, the session aborts before a single test is collected.

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
    if "@" in value:  # postgres://user:pass@host:port/db already handled above
        value = value.rsplit("@", 1)[1]
    return value.split(":")[0].strip().lower()


def _assert_local(var: str, value: str) -> None:
    lowered = value.lower()
    for needle in FORBIDDEN_SUBSTRINGS:
        if needle in lowered:
            pytest.exit(
                f"\n\nABORTED: {var} contains '{needle}'.\n"
                f"  value: {value}\n"
                f"The lab must never point at production.\n",
                returncode=3,
            )

    host = _extract_host(value)
    if host and host not in ALLOWED_HOSTS:
        pytest.exit(
            f"\n\nABORTED: {var} resolves to a non-local host '{host}'.\n"
            f"  value: {value}\n"
            f"Allowed: {', '.join(sorted(ALLOWED_HOSTS))}\n"
            f"Fix .env before running again.\n",
            returncode=3,
        )


def pytest_configure(config: pytest.Config) -> None:
    _load_dotenv()

    for var in GUARDED_VARS:
        value = os.environ.get(var)
        if value:
            _assert_local(var, value)

    # Make the cloned app importable without installing it.
    for var in ("MENTORIA_SRC", "AUTH_SRC"):
        raw = os.environ.get(var)
        if not raw:
            continue
        if not Path(raw).is_absolute():
            pytest.exit(
                f"\n\nABORTED: {var} must be an absolute path, got '{raw}'.\n"
                f"Relative paths resolve differently for pytest and for docker "
                f"compose. Use /home/<user>/lab/src/... in .env\n",
                returncode=3,
            )
        path = Path(raw)
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))

    config.stash["qalab_guard_passed"] = True


def pytest_report_header(config: pytest.Config) -> list[str]:
    return [
        f"qa-lab: host guard OK (allowed: {', '.join(sorted(ALLOWED_HOSTS))})",
        f"qa-lab: BASE_URL={os.environ.get('BASE_URL', '<unset>')} "
        f"AUTH={os.environ.get('AUTH_BASE_URL', '<unset>')}",
    ]
