#!/bin/zsh
# استاپ بات تله‌سامری

cd "/Users/omid/Downloads/Omid_Shojaei/bot python" || exit 1

if [ -f "bot.pid" ]; then
  PID=$(cat bot.pid)
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
  rm -f bot.pid
else
  echo "No pid file found. Trying to kill by name..."
  pkill -f "python main.py" 2>/dev/null || true
fi

echo "Bot stopped (if it was running)."
