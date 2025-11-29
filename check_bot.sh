#!/bin/bash
# بررسی وضعیت بات

cd "$(dirname "$0")" || exit 1

if [ -f "bot.pid" ]; then
    PID=$(cat bot.pid)
    if kill -0 "$PID" 2>/dev/null; then
        echo "✅ بات در حال اجرا است (PID: $PID)"
        echo ""
        echo "آخرین لاگ‌ها:"
        tail -5 bot.log 2>/dev/null | grep -E "INFO|ERROR|WARNING" || tail -5 bot.log
    else
        echo "❌ بات متوقف شده است (PID قدیمی: $PID)"
        rm -f bot.pid
    fi
else
    echo "❌ بات در حال اجرا نیست"
fi
