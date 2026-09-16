#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

for command_name in python3 zip unzip; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'Required command not found: %s\n' "$command_name" >&2
    exit 1
  fi
done

python3 "$ROOT/scripts/test_flow.py"

version="$(python3 - "$ROOT/plugin.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as manifest:
    print(json.load(manifest)["version"])
PY
)"
archive="$ROOT/dist/documentar-reuniao-$version.zip"
archive_paths=(
  "plugin.json"
  "assets/logo.png"
  "skills/relatorio-reuniao/SKILL.md"
  "skills/relatorio-reuniao/agents/openai.yaml"
)

for archive_path in "${archive_paths[@]}"; do
  if [[ ! -s "$ROOT/$archive_path" ]]; then
    printf 'Required archive member is missing or empty: %s\n' "$archive_path" >&2
    exit 1
  fi
done

mkdir -p "$ROOT/dist"
rm -f "$archive"
(
  cd "$ROOT"
  zip -X -q "$archive" "${archive_paths[@]}"
)

unzip -tq "$archive"
expected_listing="$(printf '%s\n' "${archive_paths[@]}")"
actual_listing="$(unzip -Z1 "$archive")"
if [[ "$actual_listing" != "$expected_listing" ]]; then
  printf 'Archive contents do not match the approved file list.\n' >&2
  exit 1
fi

printf '%s\n' "$archive"
