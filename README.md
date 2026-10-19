# qa-lab

Test suite for a local clone of two applications, MP Mentoria and
Auth-service, focused on one risk: a mentor seeing data that belongs to
another mentor.

## Why this exists

MP Mentoria is an environment where mentors record information about their
mentees and keep research project knowledge in one place. Auth-service is a
centralized application where the admin manages access for all mentors and
mentees.

This suite checks that the access guard works as defined, so mentee data stays
protected: a mentor must never see another mentor's mentee. The data is
confidential research information, so this is the highest risk in the product.

## Approach

The chosen technique is a decision table covering how MP Mentoria and
Auth-service decide access together. The table lists every combination of
token, app access, permission level and target, so no case depends on memory.
Each rule has an id (R1–R14), and the same id will appear in the test names.

Tests run at the API level. A unit test proves the guard decides correctly,
but it does not prove that every route calls the guard. API tests check what a
user actually gets, with both systems working together.

## What is covered

The access rules are defined in
[docs/decision-tables/check-scope.md](docs/decision-tables/check-scope.md):
14 rules. R13 (shared access) is still open on purpose: the code suggests
sharing works per document, not per mentee, so its expected result is TBD.

## Current status

Unit tests, run on 2026-10-19: **23 passed, 12 failed, 2 skipped.**

The 12 failures are scaffolds that raise `NotImplementedError`: tests that
were named but not written yet. They are being triaged: some will become API
scenarios, the rest will be removed with a commit explaining why.

API scenarios: not started yet (see [Next](#next)).

## How to run

Requirements: WSL2 (Ubuntu). Keep the files inside the Linux filesystem
(`~/lab`), not in `/mnt/c`: it is faster and avoids permission problems.

### Structure

```
~/lab/
├── qa-lab/          <- this repository (public, on GitHub)
│   ├── .venv/
│   ├── conftest.py  <- host lock
│   ├── tests/
│   ├── docker/
│   └── .env         <- points to ../src (absolute paths)
└── src/             <- OUTSIDE the repository, on purpose
    ├── mentoria/
    └── auth-service/
```

`src/` is a sibling of `qa-lab`, not a child. If it lived inside, one careless
`git add -f` could push the application code, and its history, to this public
repository. A separate folder makes that accident impossible, not just
unlikely.

`~/lab/qa-lab` is where you run everything: `make`, `pytest`, `git`.

### Setup

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip git make
git config --global core.autocrlf input

mkdir -p ~/lab/src
git clone <this-repo-url> ~/lab/qa-lab

cd ~/lab/qa-lab
make setup
source .venv/bin/activate
```

### Application under test

Clone **without a remote**, inside `~/lab/src`:

```bash
cd ~/lab/src
git clone --depth 1 <repo-path-mentoria> mentoria
cd mentoria && git remote remove origin

cd ~/lab/src
git clone --depth 1 <repo-path-auth> auth-service
cd auth-service && git remote remove origin
```

Extra safety for each clone:

```bash
printf '#!/bin/sh\necho "Lab guinea pig. Push blocked."\nexit 1\n' > .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

Then point `.env` to the clones using **absolute** paths:

```
MENTORIA_SRC=/home/<user>/lab/src/mentoria
AUTH_SRC=/home/<user>/lab/src/auth-service
```

Relative paths are resolved differently by `pytest` (relative to the repo) and
by `docker compose` (relative to `docker/`). Both refuse to run with a relative
path, so you don't lose a whole night on it.

The `qa-lab` repository itself is the opposite: it **does** have a remote on
GitHub, and it is public.

### Commands

```
make setup    Create the venv and install dependencies
make unit     Scope rules, no containers
```

Run `pytest` from `~/lab/qa-lab`. Running it from `~/lab` causes a collection
error.

## Isolation from production

The lab is designed so the clones never talk to production. Four layers, and
none of them trusts the others:

1. **Root `conftest.py`** aborts the session if `BASE_URL`, `AUTH_BASE_URL`,
   `POSTGRES_HOST` or `DATABASE_URL` point outside `localhost` or contain
   `perazzo.cloud`.
2. **Docker Compose** uses high ports (15432 / 18001 / 18002) bound to
   `127.0.0.1`, with its own network and volume. No `external` resources.
3. **Clones without a remote**, with a `pre-push` hook that refuses any push.
4. **Mandatory anonymization** on every dump restore. `.gitignore` blocks
   `*.dump` and `dumps/`.

> **Known gap (found 2026-10-19):** the lock checks `AUTH_BASE_URL`, but MP
> Mentoria actually reads `AUTH_SERVICE_URL`, whose default points to
> production. To be fixed before the first API test.

To check the lock works (the session must abort before any test runs):

```bash
BASE_URL=https://mentoria.perazzo.cloud pytest tests/unit
```

## Next

- API scenarios with FastAPI's `TestClient`, one per rule, using
  `pytest.mark.parametrize` with the rule ids.
- `conftest.py` fixtures for two mentors (A and B) and a token factory.
- First end-to-end flow with Playwright: log in through Auth-service, then
  open your own mentee.
- CI on GitHub Actions, running the suite on every push and pull request.