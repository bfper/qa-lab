"""Scope of GET /api/mentorandos/{id}, driven through the API.

Decision table: docs/decision-tables/check-scope.md (R5-R9).

R1 (no token) and R4 (token without access to the app) are decided inside the
real get_current_user, via auth-service introspection. The API layer replaces
that dependency with `login_as`, so those two rules need a different test
double and are not covered here yet.
"""
import pytest

OWN_EMAIL = "a@qalab.local"
OTHER_EMAIL = "b@qalab.local"
MISSING_ID = 999_999

NOT_YOURS_IS_404 = pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "ADR-Q15: another mentorando's record must return 404; check_scope "
        "returns 403 today. Remove this marker when the clone changes."
    ),
)
MISSING_IS_404 = pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "ADR-Q15: a missing record must return 404; check_scope runs before "
        "the lookup and returns 403 today. Remove this marker when the clone changes."
    ),
)


@pytest.mark.parametrize(
    "level, target, expected",
    [
        pytest.param("Editar", "own", 200, id="R5"),
        pytest.param("Editar", "other", 404, id="R6", marks=NOT_YOURS_IS_404),
        pytest.param("Gerenciar", "other", 200, id="R7"),
        pytest.param("gerenciar", "other", 404, id="R8", marks=NOT_YOURS_IS_404),
        pytest.param("Editar", "missing", 404, id="R9", marks=MISSING_IS_404),
    ],
)
def test_get_mentorando_respects_scope(
    client, login_as, make_mentorando, level, target, expected
):
    own = make_mentorando(email=OWN_EMAIL, nome="Mentorando A")
    other = make_mentorando(email=OTHER_EMAIL, nome="Mentorando B")
    records = {"own": own, "other": other}
    target_id = records[target].id if target in records else MISSING_ID

    # Control: a known-good login reads its own record. Proves the seed and
    # the fake login are wired. pytest.fail raises Failed, not AssertionError,
    # so a broken control is a real failure even inside an xfail case.
    login_as(OWN_EMAIL, level="Editar")
    if client.get(f"/api/mentorandos/{own.id}").status_code != 200:
        pytest.fail("control failed: own record not readable, check seed/login")

    login_as(OWN_EMAIL, level=level)
    response = client.get(f"/api/mentorandos/{target_id}")

    assert response.status_code == expected
    if expected == 200:
        assert response.json()["email"] == records[target].email
    else:
        assert OTHER_EMAIL not in response.text