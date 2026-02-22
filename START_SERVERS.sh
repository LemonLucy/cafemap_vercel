#!/bin/bash

# 기존 서버 종료
pkill -9 -f app_server.py 2>/dev/null
pkill -9 -f "http.server 8000" 2>/dev/null
sleep 1

cd /home/lucy/Q/coffeemap

# 백엔드 서버 (무한 재시작)
while true; do
    python3 app_server.py > server.log 2>&1
    echo "Backend crashed, restarting..." >> server.log
    sleep 2
done &

# 프론트엔드 서버 (무한 재시작)
while true; do
    python3 -m http.server 8000 > frontend.log 2>&1
    echo "Frontend crashed, restarting..." >> frontend.log
    sleep 2
done &

sleep 2

echo "🚀 CoffeeMap servers started with auto-restart"
echo "✅ Backend: http://localhost:5000"
echo "✅ Frontend: http://localhost:8000"
echo ""
echo "📝 Logs:"
echo "  - Backend: tail -f /home/lucy/Q/coffeemap/server.log"
echo "  - Frontend: tail -f /home/lucy/Q/coffeemap/frontend.log"
echo ""
echo "🛑 Stop: pkill -f app_server.py && pkill -f 'http.server 8000'"
