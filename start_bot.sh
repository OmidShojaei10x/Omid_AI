#!/bin/bash
# استارت بات تلگرام

# رفتن به دایرکتوری اسکریپت
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# فعال‌کردن venv (اگر وجود دارد)
if [ -f "venv/bin/activate" ]; then
  source "venv/bin/activate"
elif [ -f ".venv/bin/activate" ]; then
  source ".venv/bin/activate"
fi

# اگر قبلاً اجرا شده و pid مونده، کاری نکنیم
if [ -f "bot.pid" ]; then
  PID=$(cat bot.pid)
  if kill -0 "$PID" 2>/dev/null; then
    echo "Bot already running with PID $PID"
    exit 0
  else
    rm -f bot.pid
  fi
fi

# بررسی وجود فایل .env
if [ ! -f ".env" ]; then
  echo "⚠️ Warning: .env file not found!"
fi

# اجرا در پس‌زمینه + ذخیره لاگ
nohup python3 main.py > bot.log 2>&1 &
echo $! > bot.pid
echo "Bot started with PID $(cat bot.pid)"
echo "Logs are being written to bot.log"
