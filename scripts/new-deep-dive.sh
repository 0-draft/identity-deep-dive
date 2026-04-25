#!/usr/bin/env bash
# Scaffold a new deep-dive investigation.
#
# Usage:
#   ./scripts/new-deep-dive.sh <track> <topic-name>
#
# Example:
#   ./scripts/new-deep-dive.sh oauth-wg draft-ietf-oauth-v2-1

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="${REPO_ROOT}/templates/deep-dive"

if [ $# -lt 2 ]; then
  echo "Usage: $0 <track> <topic-name>"
  echo "Available tracks:"
  ls "${REPO_ROOT}/tracks/" 2>/dev/null || echo "  (none found)"
  exit 1
fi

TRACK="$1"
TOPIC="$2"
TARGET_DIR="${REPO_ROOT}/tracks/${TRACK}/deep-dives/${TOPIC}"

if [ -d "${TARGET_DIR}" ]; then
  echo "Error: ${TARGET_DIR} already exists."
  exit 1
fi

if [ ! -d "${REPO_ROOT}/tracks/${TRACK}" ]; then
  echo "Error: Track '${TRACK}' not found in tracks/."
  echo "Available tracks:"
  ls "${REPO_ROOT}/tracks/"
  exit 1
fi

cp -R "${TEMPLATE_DIR}" "${TARGET_DIR}"
echo "Created deep-dive scaffold at: ${TARGET_DIR}"
echo ""
echo "Next steps:"
echo "  1. Fill in ${TARGET_DIR}/context.md"
echo "  2. Add spec references to ${TARGET_DIR}/spec-notes.md"
echo "  3. Work through ${TARGET_DIR}/interop-checklist.md"
echo "  4. Log experiments in ${TARGET_DIR}/hands-on-log.md"
