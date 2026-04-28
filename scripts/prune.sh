#!/usr/bin/env bash
# Trim track artifacts to the canonical retention policy:
#   - reports/{daily,weekly}/ : keep latest 1 file
#   - data/raw/               : keep latest 1 entry (audit only)
#   - data/snapshots/         : keep latest 7 entries (weekly digests look back up to 7 days)
# Usage: bash scripts/prune.sh <track-dir>
set -euo pipefail
shopt -s nullglob

TRACK_DIR="${1:?track directory required (e.g. tracks/ietf-wimse)}"

prune_keep_latest() {
  local dir="$1"
  local keep="${2:-1}"
  [ -d "$dir" ] || return 0
  local entries=()
  local entry
  for entry in "$dir"/*; do
    entries+=("$(basename "$entry")")
  done
  local total=${#entries[@]}
  if [ "$total" -le "$keep" ]; then
    return 0
  fi
  local drop=$((total - keep))
  IFS=$'\n' read -r -d '' -a sorted < <(printf '%s\n' "${entries[@]}" | sort && printf '\0')
  local i
  for ((i = 0; i < drop; i++)); do
    rm -rf "${dir:?}/${sorted[i]}"
  done
  echo "pruned $drop from $dir"
}

prune_keep_latest "$TRACK_DIR/reports/daily" 1
prune_keep_latest "$TRACK_DIR/reports/weekly" 1
prune_keep_latest "$TRACK_DIR/data/raw" 1
prune_keep_latest "$TRACK_DIR/data/snapshots" 7
