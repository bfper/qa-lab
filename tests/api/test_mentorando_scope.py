"""Scope of GET /api/mentorandos/{id}, driven through the API.

Decision table: docs/decision-tables/check-scope.md (R5, R6).
"""
import pytest

OWN_EMAIL = "a@qalab.local"
OTHER_EMAIL = "b@qalab.local"


def test_mentorando_reading_own_record_gets_200(client, login_as, make_mentorando):
    own = make_mentorando(email=OWN_EMAIL, nome="Mentorando A")
    login_as(OWN_EMAIL, level="Editar")

    response = client.get(f"/api/mentorandos/{own.id}")

    assert response.status_code == 200
    assert response.json()["email"] == OWN_EMAIL


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "ADR-Q15: another mentorando's record must return 404; check_scope "
        "returns 403 today. Remove this marker when the clone changes."
    ),
)
def test_mentorando_reading_another_mentorandos_record_gets_404(
    client, login_as, make_mentorando
):
    own = make_mentorando(email=OWN_EMAIL, nome="Mentorando A")
    other = make_mentorando(email=OTHER_EMAIL, nome="Mentorando B")
    login_as(OWN_EMAIL, level="Editar")

    # Control: A can read A. Proves the seed and the fake login are wired.
    # Without it, a missing seed returns 404 "Cadastro pendente" and this
    # test would pass for the wrong reason once the marker is removed.
    assert client.get(f"/api/mentorandos/{own.id}").status_code == 200

    response = client.get(f"/api/mentorandos/{other.id}")

    assert response.status_code == 404
    assert OTHER_EMAIL not in response.text