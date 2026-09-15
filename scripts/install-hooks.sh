#!/usr/bin/env bash
# Installs a pre-commit hook for this repository.
#
# The repo is public from the first commit, so a leak is permanent: deleting
# a file in a later commit does not remove it from history. This hook blocks
# the three things that would actually hurt.
#
# Usage: ./scripts/install-hooks.sh
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOK="$REPO_ROOT/.git/hooks/pre-commit"

cat > "$HOOK" << 'HOOK_EOF'
#!/usr/bin/env bash
# qa-lab pre-commit guard. Bypass with --no-verify only if you are certain.
set -euo pipefail

staged=$(git diff --cached --name-only --diff-filter=ACM)
[ -z "$staged" ] && exit 0

fail() { echo ""; echo "COMMIT BLOCKED: $1"; echo ""; exit 1; }

# Two separate allowlists, because the two checks have different scopes.
#
# Hostnames: the guard's own config declares them, and the docs name
# production on purpose ("the lab must never reach perazzo.cloud"). Without
# this the hook blocks its own repository.
allowlisted_for_hostname() {
  case "$1" in
    conftest.py|scripts/install-hooks.sh|*.md) return 0 ;;
    *) return 1 ;;
  esac
}

# Emails: only this script, which contains the pattern itself. Markdown is
# NOT exempt — a real address in a README leaks exactly as permanently as
# one in a .py, and documentation is where an address is most likely to be
# pasted by accident.
allowlisted_for_email() {
  case "$1" in
    scripts/install-hooks.sh) return 0 ;;
    *) return 1 ;;
  esac
}

# 1. Secrets and dumps must never be committed. No allowlist, no exceptions.
for f in $staged; do
  case "$f" in
    .env|*/.env)
      fail "$f is a secrets file. Only .env.example belongs in the repo." ;;
    *.dump|*.sql.gz|dumps/*)
      fail "$f is a database dump. Dumps stay on your machine." ;;
    *id_rsa*|*.pem|*.key)
      fail "$f looks like a private key." ;;
  esac
done

for f in $staged; do
  # Strip the leading '+' of the diff: without it, a line like
  # "+@pytest.fixture" reads as the email address "+@pytest.fixture".
  added=$(git diff --cached -U0 -- "$f" | grep -E '^\+[^+]' | sed 's/^+//' || true)
  [ -z "$added" ] && continue

  # 2. Production hostnames must not appear in code or config.
  if ! allowlisted_for_hostname "$f" \
     && echo "$added" | grep -qiE 'perazzo\.cloud|srv1797282'; then
    echo "In $f:"
    echo "$added" | grep -iE 'perazzo\.cloud|srv1797282' | head -3
    fail "production hostname in $f. The lab is local-only."
  fi

  # 3. Real-looking email addresses. Test data uses @qalab.local.
  allowlisted_for_email "$f" && continue

  suspects=$(echo "$added" \
    | grep -oiE '[a-z0-9._%+-]*[a-z0-9]@[a-z0-9.-]+\.[a-z]{2,}' \
    | grep -viE '@qalab\.local|@example\.(com|org)|@exemplo\.com|@dominio\.com|noreply@|@users\.noreply\.github\.com|^git@github\.com$' \
    | sort -u || true)

  if [ -n "$suspects" ]; then
    echo "In $f:"; echo "$suspects" | head -3
    fail "real-looking email address in $f. Use @qalab.local for test data."
  fi
done

exit 0
HOOK_EOF

chmod +x "$HOOK"
echo "pre-commit hook installed at .git/hooks/pre-commit"
