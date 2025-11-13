#!/bin/bash
# Complete System Test Script

echo "🚀 Starting XSS Assistant Complete System Test"
echo "=============================================="

# Kill existing processes
echo "1. Cleaning up existing processes..."
pkill -f "vulnerable_app.py" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null
pkill -f "celery" 2>/dev/null
sleep 2

# Start services
echo "2. Starting Redis..."
redis-server --daemonize yes
sleep 1

echo "3. Starting Vulnerable Test App..."
cd /home/user/penteaser
source .venv/bin/activate
python test_app/vulnerable_app.py > /tmp/vuln_app.log 2>&1 &
sleep 3

echo "4. Starting Backend API..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
sleep 4

echo "5. Starting Celery Worker..."
cd ..
python -m celery -A workers.tasks worker --loglevel=info --concurrency=1 > /tmp/worker.log 2>&1 &
sleep 4

# Test system
echo ""
echo "6. Testing System Health..."
curl -s http://localhost:8000/health | python3 -m json.tool || echo "Backend not ready"
sleep 2

echo ""
echo "7. Creating test session for Stored XSS..."
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/sessions/ \
  -H "Content-Type: application/json" \
  -d '{"target_id": 3, "name": "Stored XSS Full Test", "description": "Testing stored/persistent XSS"}')

echo "$SESSION_RESPONSE" | python3 -m json.tool
SESSION_ID=$(echo "$SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -n "$SESSION_ID" ]; then
    echo ""
    echo "8. Waiting for scan to complete (15 seconds)..."
    sleep 15

    echo ""
    echo "9. Fetching results..."
    curl -s "http://localhost:8000/api/v1/reports/sessions/$SESSION_ID" | python3 -m json.tool

    echo ""
    echo "✅ Test Complete! Check logs:"
    echo "   - Backend: /tmp/backend.log"
    echo "   - Worker: /tmp/worker.log"
    echo "   - Vuln App: /tmp/vuln_app.log"
fi

echo ""
echo "=============================================="
echo "🎯 XSS Assistant System Test Complete"
