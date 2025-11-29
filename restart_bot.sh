#!/bin/bash
# ری‌استارت بات تله‌سامری
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

"$SCRIPT_DIR/stop_bot.sh"
sleep 1
"$SCRIPT_DIR/start_bot.sh"
