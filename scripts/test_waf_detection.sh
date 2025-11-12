#!/bin/bash
# WAF Detection Test Script

echo "🛡️  Testing WAF Detection Module"
echo "=================================="

cd /home/user/penteaser

# Test 1: Test the WAF detection module directly
echo ""
echo "1. Testing WAF detection on local vulnerable app (no WAF)..."
python3 -c "
from workers.waf_detector import quick_waf_check
import json

results = quick_waf_check('http://localhost:5000/')
print(json.dumps(results, indent=2))
"

# Test 2: Create a new session to test integrated workflow
echo ""
echo "2. Creating test session with WAF detection..."
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "target_id": 3,
    "name": "WAF Detection Test",
    "description": "Testing integrated WAF detection"
  }')

echo "$SESSION_RESPONSE" | python3 -m json.tool
SESSION_ID=$(echo "$SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -n "$SESSION_ID" ]; then
    echo ""
    echo "3. Waiting for scan to complete (20 seconds)..."
    sleep 20

    echo ""
    echo "4. Checking worker logs for WAF detection..."
    tail -30 /tmp/worker.log | grep -E "(WAF|waf|Detecting)" || echo "   No WAF messages in logs"

    echo ""
    echo "5. Fetching report to see WAF findings..."
    REPORT=$(curl -s "http://localhost:8000/api/v1/reports/sessions/$SESSION_ID")

    # Check for WAF findings
    echo "$REPORT" | python3 -c "
import sys, json
report = json.load(sys.stdin)
print(f\"Total Findings: {report['findings_count']}\")
print(\"\nAll Findings:\")
for f in report.get('findings', []):
    print(f\"  • [{f['severity'].upper()}] {f['title']}\")
    if 'WAF' in f['title'] or 'waf' in f['title'].lower():
        print(f\"    Evidence: {f.get('evidence', {})}\")
"

    echo ""
    echo "6. Full report:"
    echo "$REPORT" | python3 -m json.tool | head -60
fi

echo ""
echo "=================================="
echo "✅ WAF Detection Test Complete!"
