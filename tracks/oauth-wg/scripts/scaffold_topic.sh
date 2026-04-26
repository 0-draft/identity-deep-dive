#!/usr/bin/env bash
set -euo pipefail

RAW_NAME="${1:?draft name is required}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

SLUG="$(echo "${RAW_NAME}" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9._-')"
TOPIC_DIR="${ROOT_DIR}/deep-dives/${SLUG}"
HANDS_ON_DIR="${TOPIC_DIR}/hands-on"

mkdir -p "${HANDS_ON_DIR}"

if [[ ! -f "${TOPIC_DIR}/README.md" ]]; then
  cat > "${TOPIC_DIR}/README.md" <<EOF
# ${SLUG}

## Scope

- Draft: \`${SLUG}\`
- Datatracker: https://datatracker.ietf.org/doc/${SLUG}/

## Questions

- [ ] What problem does this draft solve?
- [ ] What are the differences from existing RFCs / drafts?
- [ ] What are the compatibility and migration considerations for implementation?
EOF
fi

if [[ ! -f "${TOPIC_DIR}/timeline.md" ]]; then
  cat > "${TOPIC_DIR}/timeline.md" <<EOF
# Timeline: ${SLUG}

| Date | Event | Source |
|---|---|---|
| TBD | initial note | manual |
EOF
fi

if [[ ! -f "${HANDS_ON_DIR}/notes.md" ]]; then
  cat > "${HANDS_ON_DIR}/notes.md" <<EOF
# Hands-on Notes: ${SLUG}

## Setup

- [ ] environment
- [ ] sample data

## Findings

- TBD
EOF
fi

echo "scaffolded topic: ${TOPIC_DIR}"
