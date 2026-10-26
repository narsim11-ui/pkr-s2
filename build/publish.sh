#!/usr/bin/env bash
# usage: PKR_PASSWORD=... build/publish.sh <dashboard index.html> <season02-sessions.json>
# Builds the page, locks it with StatiCrypt (salt in .staticrypt.json keeps "remember me" valid across updates),
# writes the locked page to ./index.html. The unlocked page and the data never enter the repo.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${PKR_PASSWORD:?set PKR_PASSWORD}"
tmp=$(mktemp -d)
python3 build/build_page.py "$1" "$2" "$tmp/index.html"
npx --yes staticrypt@3.5.4 "$tmp/index.html" -p "$PKR_PASSWORD" --short -d "$tmp/out" -c .staticrypt.json --remember 0 \
  --template-title "Poker Season 02" --template-instructions "Enter the group password." \
  --template-button "Open" --template-placeholder "Password" --template-remember "Remember on this phone" \
  --template-color-primary "#c96442" --template-color-secondary "#f5f4ef" >/dev/null
cp "$tmp/out/index.html" index.html
rm -rf "$tmp"
echo "locked page written to index.html"
