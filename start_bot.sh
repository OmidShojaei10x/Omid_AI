#!/bin/bash
# استارت بات تله‌سامری در محیط لینوکسی فعلی
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

LOG_FILE="$PROJECT_DIR/bot.log"
PID_FILE="$PROJECT_DIR/bot.pid"

# فعال‌کردن venv در صورت موجود بودن
if [[ -f "venv/bin/activate" ]]; then
  source "venv/bin/activate"
fi

# اگر قبلاً اجرا شده و pid مونده، از اجرای مجدد جلوگیری کن
if [[ -f "$PID_FILE" ]]; then
  PID="$(cat "$PID_FILE")"
  if kill -0 "$PID" 2>/dev/null; then
    echo "Bot already running with PID $PID"
    exit 0
  else
    rm -f "$PID_FILE"
  fi
fi

# اجرا در پس‌زمینه + ذخیره لاگ
nohup python3 simple_bot.py > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
echo "Bot started with PID $(cat "$PID_FILE")"
