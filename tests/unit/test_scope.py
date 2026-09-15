"""Authorization scope rules for MP Mentoria.

Rule under test (app/scope.py):
  - admin or level "Gerenciar" -> access to every mentorando
  - any other level           -> access only to the Mentorando whose `email`
                                 matches the logged-in user's email
  - mismatch                  -> HTTPException 403
  - no matching cadastro      -> HTTPException 404

Two functions are covered: check_scope (single owner) and
check_acesso_compartilhavel (v1.5, owner + shared-access list).

HOW TO WORK THROUGH THIS FILE
  Cases are named and their expected outcome is declared in the matrix.
  The bodies are yours to write. TEST_ID_TEMPLATE below is fully written as
  a reference — follow its shape, do not copy its assertions blindly.
"""
import pytest
from fastapi import HTTPException

from app.scope import (
    check_acesso_compartilhavel,
    check_scope,
    get_proprio_mentorando,
    is_gerente,
    require_gerente,
)

pytestmark = pytest.mark.unit

OWNER_EMAIL = "owner@qalab.local"
OTHER_EMAIL = "other@qalab.local"


# ---------------------------------------------------------------------------
# is_gerente — cheapest surface, run it first
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "level, is_admin, expected",
    [
        pytest.param("Gerenciar", False, True, id="level_gerenciar_is_manager"),
        pytest.param("Editar", False, False, id="level_editar_is_not_manager"),
        pytest.param("Visualizar", False, False, id="level_visualizar_is_not_manager"),
        pytest.param("Visualizar", True, True, id="admin_flag_overrides_level"),
        pytest.param("", False, False, id="empty_level_is_not_manager"),
        pytest.param(None, False, False, id="null_level_is_not_manager"),
        # The next three probe normalization. Production compares the string
        # exactly, so decide what SHOULD happen before you assert.
        pytest.param("  Gerenciar  ", False, True, id="level_with_surrounding_spaces"),
        pytest.param("gerenciar", False, None, id="level_lowercase_UNDECIDED"),
        pytest.param("GERENCIAR", False, None, id="level_uppercase_UNDECIDED"),
    ],
)
def test_is_gerente(make_user, level, is_admin, expected):
    """REFERENCE IMPLEMENTATION — the rest of this file follows this shape."""
    if expected is None:
        pytest.skip("decide the intended behaviour, then replace None in the matrix")

    user = make_user(level=level, is_admin=is_admin)

    assert is_gerente(user) is expected


# ---------------------------------------------------------------------------
# check_scope — the rule that keeps one mentorando out of another's data
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "level, is_admin, target, expected_status",
    [
        # Managers pass regardless of target.
        pytest.param("Gerenciar", False, "own", None, id="manager_reaches_own_record"),
        pytest.param("Gerenciar", False, "other", None, id="manager_reaches_other_record"),
        pytest.param("Gerenciar", False, "missing", None, id="manager_reaches_unknown_id"),
        pytest.param("Visualizar", True, "other", None, id="admin_reaches_other_record"),

        # Regular users: own record only.
        pytest.param("Visualizar", False, "own", None, id="viewer_reaches_own_record"),
        pytest.param("Editar", False, "own", None, id="editor_reaches_own_record"),
        pytest.param("Visualizar", False, "other", 403, id="viewer_blocked_from_other_record"),
        pytest.param("Editar", False, "other", 403, id="editor_blocked_from_other_record"),
        pytest.param("Visualizar", False, "missing", 403, id="viewer_blocked_from_unknown_id"),
    ],
)
def test_check_scope_by_role_and_target(
    session, make_user, make_mentorando, level, is_admin, target, expected_status
):
    """expected_status None means the call must return without raising."""
    owner = make_mentorando(email=OWNER_EMAIL)
    other = make_mentorando(email=OTHER_EMAIL)
    target_id = {"own": owner.id, "other": other.id, "missing": 999_999}[target]
    user = make_user(email=OWNER_EMAIL, level=level, is_admin=is_admin)

    # TODO: call check_scope(session, user, target_id).
    # When expected_status is None it must return None.
    # Otherwise it must raise HTTPException with that status_code.
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Email normalization — where the real bug is likely to be
#
# get_proprio_mentorando lowercases and strips the LOGIN email, but compares
# it against the STORED email as-is. If a Mentorando was ever saved with a
# capital letter or a trailing space, the lookup misses and a legitimate user
# is turned away with 404 "Cadastro pendente".
#
# Verify against the real database before filing this as a bug — check
# whether the cadastro path normalizes on write.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "stored_email, login_email, expect_found",
    [
        pytest.param("owner@qalab.local", "owner@qalab.local", True, id="exact_match"),
        pytest.param("owner@qalab.local", "OWNER@QALAB.LOCAL", True, id="login_uppercase_is_normalized"),
        pytest.param("owner@qalab.local", "  owner@qalab.local  ", True, id="login_padded_is_normalized"),
        pytest.param("Owner@QALab.local", "owner@qalab.local", None, id="stored_uppercase_SUSPECTED_BUG"),
        pytest.param("owner@qalab.local ", "owner@qalab.local", None, id="stored_trailing_space_SUSPECTED_BUG"),
    ],
)
def test_get_proprio_mentorando_email_normalization(
    session, make_user, make_mentorando, stored_email, login_email, expect_found
):
    if expect_found is None:
        pytest.skip("run it, observe the real behaviour, then decide: bug or by design")

    make_mentorando(email=stored_email)
    user = make_user(email=login_email, level="Visualizar")

    # TODO: call get_proprio_mentorando(session, user).
    # expect_found True  -> returns the Mentorando
    # expect_found False -> raises HTTPException 404
    raise NotImplementedError


@pytest.mark.parametrize(
    "login_email",
    [
        pytest.param("", id="empty_login_email"),
        pytest.param(None, id="null_login_email"),
        pytest.param("ghost@qalab.local", id="login_email_without_cadastro"),
    ],
)
def test_get_proprio_mentorando_without_cadastro(
    session, make_user, make_mentorando, login_email
):
    """No cadastro must be 404 with the friendly message, never 500."""
    make_mentorando(email=OWNER_EMAIL)
    user = make_user(email=login_email, level="Visualizar")

    # TODO: assert HTTPException 404.
    # Then assert the detail message — it is user-facing copy and a silent
    # change to it is a regression the front-end will not catch.
    raise NotImplementedError


# ---------------------------------------------------------------------------
# require_gerente — an "Editar" user passes require_write but must fail here
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "level, is_admin, expected_status",
    [
        pytest.param("Gerenciar", False, None, id="manager_allowed"),
        pytest.param("Visualizar", True, None, id="admin_allowed"),
        pytest.param("Editar", False, 403, id="editor_blocked_from_manager_action"),
        pytest.param("Visualizar", False, 403, id="viewer_blocked_from_manager_action"),
    ],
)
def test_require_gerente(make_user, level, is_admin, expected_status):
    user = make_user(level=level, is_admin=is_admin)

    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# check_acesso_compartilhavel — v1.5 variant, owner OR shared-access list
#
# Same shape as check_scope with one extra dimension. The trap: an empty
# list and a list containing an unrelated id must both still block.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "level, is_admin, owner, shared, expected_status",
    [
        pytest.param("Gerenciar", False, "other", "none", None, id="manager_reaches_any_document"),
        pytest.param("Visualizar", False, "own", "none", None, id="viewer_reaches_own_document"),
        pytest.param("Visualizar", False, "other", "self", None, id="viewer_reaches_shared_document"),
        pytest.param("Visualizar", False, "other", "none", 403, id="viewer_blocked_no_sharing"),
        pytest.param("Visualizar", False, "other", "stranger", 403, id="viewer_blocked_shared_with_someone_else"),
        pytest.param("Editar", False, "other", "none", 403, id="editor_blocked_no_sharing"),
    ],
)
def test_check_acesso_compartilhavel(
    session, make_user, make_mentorando, level, is_admin, owner, shared, expected_status
):
    me = make_mentorando(email=OWNER_EMAIL)
    them = make_mentorando(email=OTHER_EMAIL)
    owner_id = me.id if owner == "own" else them.id
    ids_com_acesso = {"none": [], "self": [me.id], "stranger": [999_999]}[shared]
    user = make_user(email=OWNER_EMAIL, level=level, is_admin=is_admin)

    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Regression anchor for week 5
#
# Every router calls check_scope with an id taken from the request body or
# from a row it just loaded. In documentos.py and referencias.py the call is
# nested inside an `if` — read those two paths before trusting them, and
# reproduce whatever you find here as a named test.
# ---------------------------------------------------------------------------
