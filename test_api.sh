#!/bin/bash

# Set the base URL (local by default, can be overridden)
BASE_URL=${1:-"http://127.0.0.1:8000"}

echo "Using Base URL: $BASE_URL"
echo "-----------------------------------"

# 1. Anonymous visitor tracking
echo "1. Tracking anonymous visitor (cookie_id: anon_999)..."
curl -s -X POST "$BASE_URL/track" \
     -H "Content-Type: application/json" \
     -d '{
       "identifiers": [{"type": "cookie_id", "value": "anon_999"}],
       "traits": [{"type": "ip", "value": "10.0.0.1"}, {"type": "fingerprint", "value": "fp_blue"}],
       "event": {"event_type": "page_view", "category": "Fashion"}
     }' | jq .

echo -e "\n"

# 2. Link Email to anonymous profile
echo "2. Linking email 'jane@test.com' to anon_999..."
curl -s -X POST "$BASE_URL/track" \
     -H "Content-Type: application/json" \
     -d '{
       "identifiers": [
         {"type": "cookie_id", "value": "anon_999"},
         {"type": "email", "value": "jane@test.com"}
       ],
       "event": {"event_type": "product_view", "category": "Fashion"}
     }' | jq .

echo -e "\n"

# 3. Upgrade to Loyalty Member
echo "3. Upgrading 'jane@test.com' to Loyalty ID 'L_GOLD_1'..."
curl -s -X POST "$BASE_URL/track" \
     -H "Content-Type: application/json" \
     -d '{
       "identifiers": [
         {"type": "email", "value": "jane@test.com"},
         {"type": "loyalty_id", "value": "L_GOLD_1"}
       ],
       "event": {"event_type": "purchase", "category": "Fashion"}
     }' | jq .

echo -e "\n"

# 4. Probabilistic Merge (Same IP + Fingerprint, different cookie)
echo "4. Tracking another device with same IP/FP (cookie_id: device_tablet)..."
curl -s -X POST "$BASE_URL/track" \
     -H "Content-Type: application/json" \
     -d '{
       "identifiers": [{"type": "cookie_id", "value": "device_tablet"}],
       "traits": [{"type": "ip", "value": "10.0.0.1"}, {"type": "fingerprint", "value": "fp_blue"}],
       "event": {"event_type": "page_view", "category": "Home"}
     }' | jq .

echo -e "\n"

# 5. Get the final unified profile
echo "5. Retrieving final unified profile for 'L_GOLD_1'..."
curl -s "$BASE_URL/profile/loyalty_id/L_GOLD_1" | jq .
