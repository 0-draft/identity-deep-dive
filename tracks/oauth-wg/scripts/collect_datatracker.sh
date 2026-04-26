#!/usr/bin/env bash
set -euo pipefail

OUTDIR="${1:?output directory is required}"
mkdir -p "${OUTDIR}"

echo "[datatracker] collecting group metadata"
curl -fsSL "https://datatracker.ietf.org/api/v1/group/group/?acronym=oauth&format=json" > "${OUTDIR}/group.json"

echo "[datatracker] collecting state taxonomy"
curl -fsSL "https://datatracker.ietf.org/api/v1/doc/state/?format=json&limit=1000" > "${OUTDIR}/states.json"

echo "[datatracker] collecting active oauth drafts"
curl -fsSL "https://datatracker.ietf.org/api/v1/doc/document/?group__acronym=oauth&name__contains=draft-ietf-oauth-&states=1&limit=200&format=json" > "${OUTDIR}/oauth_drafts_active.json"

echo "[datatracker] collecting documents page"
curl -fsSL "https://datatracker.ietf.org/wg/oauth/documents/" > "${OUTDIR}/documents.html"

echo "[datatracker] collecting meetings page"
curl -fsSL "https://datatracker.ietf.org/wg/oauth/meetings/" > "${OUTDIR}/meetings.html"
