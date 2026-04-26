#!/usr/bin/env bash
# Trim track artifacts to the canonical retention policy:
#   - reports/{daily,weekly}/ : keep latest 1 file
#   - data/snapshots/, data/raw/ : keep latest 1 entry
#   - data/normalized/<prefix>-<YYYY-MM-DD>.json : keep latest 7 per prefix
#     (weekly reports may need recent dated history; non-dated files are left alone)
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

# For files like <prefix>-<YYYY-MM-DD>.json under a directory, keep the latest N per prefix.
prune_dated_normalized() {
  local dir="$1"
  local keep="${2:-7}"
  [ -d "$dir" ] || return 0
  local file base prefix
  local raw_prefixes=()
  for file in "$dir"/*-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json; do
    base=$(basename "$file")
    prefix=${base%-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json}
    raw_prefixes+=("$prefix")
  done
  [ ${#raw_prefixes[@]} -eq 0 ] && return 0
  local prefixes=()
  IFS=$'\n' read -r -d '' -a prefixes < <(printf '%s\n' "${raw_prefixes[@]}" | sort -u && printf '\0')
  for prefix in "${prefixes[@]}"; do
    local matches=()
    for file in "$dir"/"$prefix"-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json; do
      matches+=("$(basename "$file")")
    done
    local total=${#matches[@]}
    if [ "$total" -le "$keep" ]; then continue; fi
    local drop=$((total - keep))
    IFS=$'\n' read -r -d '' -a sorted < <(printf '%s\n' "${matches[@]}" | sort && printf '\0')
    local i
    for ((i = 0; i < drop; i++)); do
      rm -f "${dir:?}/${sorted[i]}"
    done
    echo "pruned $drop ${prefix}-* files from $dir"
  done
}

prune_keep_latest "$TRACK_DIR/reports/daily" 1
prune_keep_latest "$TRACK_DIR/reports/weekly" 1
prune_keep_latest "$TRACK_DIR/data/snapshots" 1
prune_keep_latest "$TRACK_DIR/data/raw" 1
prune_dated_normalized "$TRACK_DIR/data/normalized" 7
