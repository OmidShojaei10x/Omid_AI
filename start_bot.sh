#!/bin/bash
# استارت بات تلگرام

# رفتن به دایرکتوری اسکریپت
cd "$(dirname "$0")" || exit 1

# فعال‌کردن venv (اگر وجود داشته باشد)
if [ -f "venv/bin/activate" ]; then
  source "venv/bin/activate"
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

# اجرا در پس‌زمینه + ذخیره لاگ
nohup python3 main.py > bot.log 2>&1 &
echo $! > bot.pid
echo "Bot started with PID $(cat bot.pid)"
