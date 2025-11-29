#!/bin/bash
# استارت بات ساده

cd /workspace || exit 1

# بررسی اگر بات در حال اجراست
if [ -f "simple_bot.pid" ]; then
  PID=$(cat simple_bot.pid)
  if kill -0 "$PID" 2>/dev/null; then
    echo "Bot is already running with PID $PID"
    exit 0
  else
    rm -f simple_bot.pid
  fi
fi

# نصب وابستگی‌ها
echo "Installing dependencies..."
pip install -q python-telegram-bot

# اجرا در پس‌زمینه + ذخیره لاگ
nohup python3 simple_bot.py > simple_bot.log 2>&1 &
echo $! > simple_bot.pid
echo "✅ Bot started with PID $(cat simple_bot.pid)"
echo "📝 Logs: tail -f /workspace/simple_bot.log"
