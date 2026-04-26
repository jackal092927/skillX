#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${SKILLX_FALLBACK_CLAUDE_CONFIG_DIR:-$HOME/.claude-skillx-fallback}"
TOKEN_PATH="${SKILLX_FALLBACK_CLAUDE_OAUTH_FILE:-$CONFIG_DIR/claude-code-oauth-token}"

cat <<EOF
This will authenticate the SkillX fallback Claude Code account in an isolated config dir.

  config_dir: $CONFIG_DIR
  token_path: $TOKEN_PATH

Use your secondary Claude account in the browser/auth flow.
EOF

mkdir -p "$CONFIG_DIR"
CLAUDE_CONFIG_DIR="$CONFIG_DIR" claude setup-token

if [[ ! -f "$TOKEN_PATH" ]]; then
  cat >&2 <<EOF

Expected token file was not found:
  $TOKEN_PATH

If Claude Code wrote the token elsewhere, move or copy that token file to the path above,
or pass it explicitly with:
  SKILLX_FALLBACK_CLAUDE_OAUTH_FILE=/path/to/claude-code-oauth-token
EOF
  exit 1
fi

chmod 600 "$TOKEN_PATH"
echo
echo "Fallback Claude auth is ready:"
echo "  $TOKEN_PATH"
