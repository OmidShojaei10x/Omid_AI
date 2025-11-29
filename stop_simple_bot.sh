#!/bin/bash
# متوقف کردن بات ساده

cd /workspace || exit 1

if [ -f "simple_bot.pid" ]; then
  PID=$(cat simple_bot.pid)
  if kill -0 "$PID" 2>/dev/null; then
    kill "$PID"
    rm -f simple_bot.pid
    echo "✅ Bot stopped (PID $PID)"
  else
    echo "⚠️ Bot is not running"
    rm -f simple_bot.pid
  fi
else
  echo "⚠️ No PID file found"
fi
