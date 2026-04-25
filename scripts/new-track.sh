#!/usr/bin/env bash
# Scaffold a new monitoring track.
#
# Usage:
#   ./scripts/new-track.sh <track-name>
#
# Example:
#   ./scripts/new-track.sh ietf-ace

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="${REPO_ROOT}/templates/new-track"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <track-name>"
  exit 1
fi

TRACK="$1"
TARGET_DIR="${REPO_ROOT}/tracks/${TRACK}"

if [ -d "${TARGET_DIR}" ]; then
  echo "Error: ${TARGET_DIR} already exists."
  exit 1
fi

cp -R "${TEMPLATE_DIR}" "${TARGET_DIR}"
echo "Created track scaffold at: ${TARGET_DIR}"
echo ""
echo "Next steps:"
echo "  1. Edit ${TARGET_DIR}/config/sources.yaml with your data sources"
echo "  2. Edit ${TARGET_DIR}/config/scoring.yaml to tune weights"
echo "  3. Implement collection scripts in ${TARGET_DIR}/scripts/"
echo "  4. Add a workflow entry in .github/workflows/"
