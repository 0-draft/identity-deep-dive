#!/usr/bin/env bash
set -euo pipefail

OUTDIR="${1:?output directory is required}"
mkdir -p "${OUTDIR}"

echo "[mailarchive] collecting oauth list index"
curl -fsSL "https://mailarchive.ietf.org/arch/browse/oauth/" > "${OUTDIR}/browse_oauth.html"
