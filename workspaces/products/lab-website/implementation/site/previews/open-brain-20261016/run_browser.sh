#!/usr/bin/env bash
set -euo pipefail
export LD_LIBRARY_PATH="/home/vlad_/.cache/ms-playwright/user-libs/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec /mnt/c/Users/vlad_/.codex/skills/playwright/scripts/playwright_cli.sh "$@"
