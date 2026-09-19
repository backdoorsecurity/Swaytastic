#!/bin/bash
# Switch the installed Swaytastic look to a pack in local/packs/.
# Usage: switch-theme.sh [pack]
#        switch-theme.sh --list
set -euo pipefail

REPO="${SWAYTASTIC_ROOT:-$HOME/Swaytastic}"
APPLY="$REPO/local/apply-pack.py"

if [[ ! -x "$APPLY" && ! -f "$APPLY" ]]; then
  echo "apply-pack.py not found at $APPLY" >&2
  echo "set SWAYTASTIC_ROOT to the repo clone" >&2
  exit 1
fi

if [[ "${1:-}" == "--list" || "${1:-}" == "-l" || $# -eq 0 ]]; then
  python3 "$APPLY" --list
  if [[ $# -eq 0 ]]; then
    echo "usage: $0 <pack>" >&2
    exit 0
  fi
  exit 0
fi

PACK="$1"
python3 "$APPLY" "$PACK" --live --repo --root "$REPO" --reload
echo "active pack: $PACK"
