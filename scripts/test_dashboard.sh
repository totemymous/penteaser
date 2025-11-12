#!/bin/bash
# Dashboard Functionality Test Script

echo "🎯 Testing XSS Assistant Dashboard"
echo "===================================="

API_BASE="http://localhost:8000/api/v1"

# Test 1: Dashboard loads
echo ""
echo "1. Testing dashboard homepage..."
DASHBOARD=$(curl -s http://localhost:8000/ | grep -c "XSS Assistant Dashboard")
if [ "$DASHBOARD" -gt 0 ]; then
    echo "   ✅ Dashboard HTML loads successfully"
else
    echo "   ❌ Dashboard failed to load"
    exit 1
fi

# Test 2: Get targets
echo ""
echo "2. Testing GET /api/v1/targets/..."
TARGETS=$(curl -s "$API_BASE/targets/" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "   ✅ Found $TARGETS targets"

# Test 3: Get sessions
echo ""
echo "3. Testing GET /api/v1/sessions/..."
SESSIONS=$(curl -s "$API_BASE/sessions/" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "   ✅ Found $SESSIONS sessions"

# Test 4: Create new target
echo ""
echo "4. Testing POST /api/v1/targets/ (Create Target)..."
TARGET_RESPONSE=$(curl -s -X POST "$API_BASE/targets/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Dashboard Target",
    "url": "http://localhost:5000/",
    "description": "Created from dashboard test"
  }')
TARGET_ID=$(echo "$TARGET_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
if [ -n "$TARGET_ID" ]; then
    echo "   ✅ Target created with ID: $TARGET_ID"
else
    echo "   ❌ Failed to create target"
    echo "$TARGET_RESPONSE"
    exit 1
fi

# Test 5: Start scan (create session)
echo ""
echo "5. Testing POST /api/v1/sessions/ (Start Scan)..."
SESSION_RESPONSE=$(curl -s -X POST "$API_BASE/sessions/" \
  -H "Content-Type: application/json" \
  -d "{
    \"target_id\": $TARGET_ID,
    \"name\": \"Dashboard Test Scan\",
    \"description\": \"Automated scan from dashboard test\"
  }")
SESSION_ID=$(echo "$SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
if [ -n "$SESSION_ID" ]; then
    echo "   ✅ Scan started with Session ID: $SESSION_ID"
else
    echo "   ❌ Failed to start scan"
    echo "$SESSION_RESPONSE"
    exit 1
fi

# Test 6: Wait for scan to complete
echo ""
echo "6. Waiting for scan to complete (15 seconds)..."
sleep 15

# Test 7: Get report
echo ""
echo "7. Testing GET /api/v1/reports/sessions/$SESSION_ID (View Report)..."
REPORT=$(curl -s "$API_BASE/reports/sessions/$SESSION_ID")
FINDINGS=$(echo "$REPORT" | python3 -c "import sys, json; print(json.load(sys.stdin)['findings_count'])" 2>/dev/null)
if [ -n "$FINDINGS" ]; then
    echo "   ✅ Report generated with $FINDINGS findings"

    # Show findings summary
    echo ""
    echo "   Findings Summary:"
    echo "$REPORT" | python3 -c "
import sys, json
report = json.load(sys.stdin)
for f in report.get('findings', []):
    severity = f['severity'].upper()
    title = f['title']
    print(f'   • [{severity}] {title}')
"
else
    echo "   ❌ Failed to get report"
fi

# Test 8: Check metrics
echo ""
echo "8. Testing dashboard metrics calculation..."
NEW_TARGET_COUNT=$(curl -s "$API_BASE/targets/" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
NEW_SESSION_COUNT=$(curl -s "$API_BASE/sessions/" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "   ✅ Total Targets: $NEW_TARGET_COUNT"
echo "   ✅ Total Sessions: $NEW_SESSION_COUNT"

# Test 9: Check dashboard JavaScript loads
echo ""
echo "9. Testing dashboard JavaScript file..."
JS_FILE=$(curl -s http://localhost:8000/static/dashboard.js | grep -c "API_BASE")
if [ "$JS_FILE" -gt 0 ]; then
    echo "   ✅ Dashboard JavaScript loads successfully"
else
    echo "   ❌ Dashboard JavaScript not found"
fi

echo ""
echo "===================================="
echo "✅ Dashboard Functionality Test Complete!"
echo ""
echo "Dashboard URL: http://localhost:8000/"
echo "API Documentation: http://localhost:8000/docs"
echo ""
