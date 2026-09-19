#!/bin/bash
# MesloLGS NF — the font Powerlevel10k's glyph tests expect.
set -euo pipefail

DEST="${MESLO_DIR:-$HOME/.local/share/fonts}"
BASE="https://github.com/romkatv/powerlevel10k-media/raw/master"
files=(
  "MesloLGS NF Regular.ttf"
  "MesloLGS NF Bold.ttf"
  "MesloLGS NF Italic.ttf"
  "MesloLGS NF Bold Italic.ttf"
)

mkdir -p "$DEST"
need=0
for f in "${files[@]}"; do
  if [[ ! -s "$DEST/$f" ]]; then
    need=1
    break
  fi
done

if [[ $need -eq 0 ]]; then
  echo "MesloLGS NF already in $DEST"
  exit 0
fi

echo "installing MesloLGS NF into $DEST"
for f in "${files[@]}"; do
  if [[ -s "$DEST/$f" ]]; then
    continue
  fi
  echo "  $f"
  curl -fsSL --output "$DEST/$f" "$BASE/${f// /%20}"
done
fc-cache -f "$DEST"
echo "MesloLGS NF ready"
