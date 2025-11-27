#!/bin/zsh
# استارت بات تله‌سامری

cd "/Users/omid/Downloads/Omid_Shojaei/bot python" || exit 1

# فعال‌کردن venv
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
nohup python main.py > bot.log 2>&1 &
echo $! > bot.pid
echo "Bot started with PID $(cat bot.pid)"
