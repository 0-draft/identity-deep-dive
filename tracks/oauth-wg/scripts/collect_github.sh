#!/usr/bin/env bash
set -euo pipefail

OUTDIR="${1:?output directory is required}"
mkdir -p "${OUTDIR}"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh command is required" >&2
  exit 1
fi

echo "[github] collecting repos"
gh api -X GET orgs/oauth-wg/repos --paginate -f per_page=100 -f type=public > "${OUTDIR}/repos.json"

echo "[github] collecting organization events"
gh api -X GET orgs/oauth-wg/events > "${OUTDIR}/org_events.json"

echo "[github] collecting recent pull requests"
gh api -X GET "search/issues?q=org:oauth-wg+is:pr&per_page=100&sort=updated&order=desc" > "${OUTDIR}/prs_recent.json"

echo "[github] collecting recent issues"
gh api -X GET "search/issues?q=org:oauth-wg+is:issue&per_page=100&sort=updated&order=desc" > "${OUTDIR}/issues_recent.json"
