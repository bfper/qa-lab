"""Smoke test: proves the pytest toolchain itself is working."""

import pytest


@pytest.mark.unit
def test_pytest_runner_evaluates_assertions():
    result = 1 + 1

    assert result == 2