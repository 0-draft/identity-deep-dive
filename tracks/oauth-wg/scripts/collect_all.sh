#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TIMESTAMP="${1:-$(date -u +%Y-%m-%dT%H%M%SZ)}"
SNAPSHOT_DIR="${ROOT_DIR}/data/snapshots/${TIMESTAMP}"

mkdir -p "${SNAPSHOT_DIR}/github" "${SNAPSHOT_DIR}/datatracker" "${SNAPSHOT_DIR}/mailarchive"

"${ROOT_DIR}/scripts/collect_github.sh" "${SNAPSHOT_DIR}/github"
"${ROOT_DIR}/scripts/collect_datatracker.sh" "${SNAPSHOT_DIR}/datatracker"
"${ROOT_DIR}/scripts/collect_mailarchive.sh" "${SNAPSHOT_DIR}/mailarchive"

printf "%s\n" "${TIMESTAMP}" > "${ROOT_DIR}/data/history/latest_snapshot.txt"
echo "snapshot: ${SNAPSHOT_DIR}"
