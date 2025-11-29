#!/bin/bash
# استاپ بات تله‌سامری
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

PID_FILE="$PROJECT_DIR/bot.pid"

if [[ -f "$PID_FILE" ]]; then
  PID="$(cat "$PID_FILE")"
  if kill -0 "$PID" 2>/dev/null; then
    echo "Stopping bot with PID $PID..."
    kill "$PID"
    sleep 1
    if kill -0 "$PID" 2>/dev/null; then
      echo "Force killing bot..."
      kill -9 "$PID"
    fi
  else
    echo "PID file exists but process is not running."
  fi
  rm -f "$PID_FILE"
else
  echo "No pid file found. Trying to kill by name..."
  pkill -f "python3 main.py" 2>/dev/null || true
fi

echo "Bot stopped (if it was running)."
