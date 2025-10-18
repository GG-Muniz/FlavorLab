#!/bin/bash
# Test script to call the LLM meal plan API endpoint

# First, login to get a token
echo "=== Logging in ==="
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "g.garcia.9816@gmial.com", "password": "password123"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "Failed to get auth token"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✓ Logged in successfully"
echo ""

# Call the LLM meal plan endpoint
echo "=== Generating LLM Meal Plan (without recipes) ==="
curl -s -X POST http://localhost:8000/api/v1/users/me/llm-meal-plan?include_recipes=false \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool

echo ""
echo "=== Test Complete ==="
