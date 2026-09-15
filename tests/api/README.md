# API — week 5

Postman collection per service (auth, mentoria), environment with base_url
and token, assertions on status, body schema and values.

Edge cases per endpoint: 401 without token, 403 with another mentor's token
(check_scope again, now at the boundary), 422 with invalid payload, 404.

Architecture decision to write down: what stays in Postman (living
documentation and exploration) and what stays in pytest + httpx (regression
that runs in CI). Both answers are defensible — having yours, written, is
what counts.
