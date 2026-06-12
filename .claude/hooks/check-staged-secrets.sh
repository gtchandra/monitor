#!/usr/bin/env bash
# PreToolUse hook: scan staged changes for secrets and personal information
# before a `git commit`. Exit 2 blocks the commit (stderr is shown to Claude).
#
# Reads the hook payload JSON on stdin; only acts on `git commit` commands.
set -euo pipefail

payload="$(cat)"
cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // ""')"

# Only guard actual commit commands. Let everything else through untouched.
case "$cmd" in
  *"git commit"*|*"git "*"commit"*) ;;
  *) exit 0 ;;
esac

# Inspect what is actually staged (added lines only).
diff="$(git diff --cached --no-color -U0 2>/dev/null | grep -E '^\+' | grep -vE '^\+\+\+' || true)"
[ -z "$diff" ] && exit 0

declare -a hits=()
add_hit() { hits+=("  - $1"); }

scan() { # scan <label> <regex>
  if printf '%s' "$diff" | grep -nEi "$2" >/dev/null 2>&1; then
    add_hit "$1"
  fi
}

# --- Secrets / credentials -------------------------------------------------
scan "Private key block"            '-----BEGIN [A-Z ]*PRIVATE KEY-----'
scan "AWS access key id"            'AKIA[0-9A-Z]{16}'
scan "AWS secret access key"        'aws_secret_access_key[[:space:]]*[=:]'
scan "Generic API key / secret"     '(api[_-]?key|secret|client[_-]?secret|access[_-]?token)[[:space:]]*[=:][[:space:]]*["'"'"']?[A-Za-z0-9/_+-]{16,}'
scan "Password assignment"          '(password|passwd|pwd)[[:space:]]*[=:][[:space:]]*["'"'"']?[^[:space:]"'"'"']{6,}'
scan "Bearer token"                 'bearer[[:space:]]+[A-Za-z0-9._-]{20,}'
scan "Authorization header"         'authorization[[:space:]]*[=:]'
scan "GitHub token"                 'gh[pousr]_[A-Za-z0-9]{20,}'
scan "Slack token"                  'xox[baprs]-[A-Za-z0-9-]{10,}'
scan "Google API key"               'AIza[0-9A-Za-z_-]{35}'
scan "OpenAI / sk- key"             'sk-[A-Za-z0-9]{20,}'
scan "Private key in env var"       '(PRIVATE_KEY|SECRET_KEY|ACCESS_KEY)[[:space:]]*='

# --- Personal information --------------------------------------------------
# local-part must start alphanumeric → avoids matching diff-prefixed decorators like "+@app.route"
scan "Email address"                '[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
scan "Phone number"                 '(\+?[0-9]{1,3}[ .-]?)?\(?[0-9]{2,4}\)?[ .-]?[0-9]{3,4}[ .-]?[0-9]{3,4}'
scan "Credit card number"           '\b([0-9]{4}[ -]?){3}[0-9]{4}\b'
scan "IBAN"                          '\b[A-Z]{2}[0-9]{2}[ ]?([A-Z0-9]{4}[ ]?){2,7}[A-Z0-9]{1,4}\b'
scan "Italian fiscal code"          '\b[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]\b'

if [ ${#hits[@]} -gt 0 ]; then
  {
    echo "BLOCKED: staged changes look like they contain secrets or personal information."
    echo "Matched patterns:"
    printf '%s\n' "${hits[@]}"
    echo ""
    echo "Review with: git diff --cached"
    echo "If this is a false positive, unstage/sanitize the content, or bypass intentionally"
    echo "by committing outside this hook (e.g. git commit --no-verify is NOT honored here —"
    echo "remove or adjust the pattern in .claude/hooks/check-staged-secrets.sh)."
  } >&2
  exit 2
fi

exit 0
