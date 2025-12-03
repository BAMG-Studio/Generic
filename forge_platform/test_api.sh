#!/bin/bash
# Quick API test script

API_URL="http://localhost:8000/api/v1"

echo "🧪 Testing ForgeTrace API..."
echo ""

# Health check
echo "1. Health Check"
curl -s $API_URL/../health | jq
echo ""

# Login (you'll need to create a user first)
echo "2. Login (update credentials)"
echo "   Run: docker-compose exec backend python cli.py create-user"
echo ""

# Example with token
TOKEN="your_token_here"

echo "3. Get Usage Stats"
curl -s -H "Authorization: Bearer $TOKEN" $API_URL/usage/stats | jq
echo ""

echo "4. List Audits"
curl -s -H "Authorization: Bearer $TOKEN" $API_URL/audits | jq
echo ""

echo "5. Submit Audit"
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"repository": "https://github.com/django/django"}' \
  $API_URL/audits | jq
echo ""

echo "6. List Tokens"
curl -s -H "Authorization: Bearer $TOKEN" $API_URL/tokens | jq
echo ""

echo "✅ API tests complete!"
