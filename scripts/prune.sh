#!/usr/bin/env bash
# Keep only the latest entry under each track artifact directory.
# Usage: bash scripts/prune.sh <track-dir>
set -euo pipefail

TRACK_DIR="${1:?track directory required (e.g. tracks/ietf-wimse)}"

prune_keep_latest() {
  local dir="$1"
  local keep="${2:-1}"
  [ -d "$dir" ] || return 0
  local total
  total=$(ls -1 "$dir" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$total" -le "$keep" ]; then
    return 0
  fi
  local drop=$((total - keep))
  ls -1 "$dir" | sort | head -n "$drop" | while read -r entry; do
    rm -rf "$dir/$entry"
  done
  echo "pruned $drop from $dir"
}

prune_keep_latest "$TRACK_DIR/reports/daily" 1
prune_keep_latest "$TRACK_DIR/reports/weekly" 1
prune_keep_latest "$TRACK_DIR/data/snapshots" 1
prune_keep_latest "$TRACK_DIR/data/raw" 1
