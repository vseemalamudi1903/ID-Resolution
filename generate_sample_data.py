import json
import random
import uuid

def generate_data(num_users=50, events_per_user=20):
    events = []

    categories = ["Electronics", "Fashion", "Home", "Garden", "Sports", "Beauty"]
    event_types = ["page_view", "product_view", "customer_review", "purchase", "client_event"]

    for i in range(num_users):
        # Initial state: Anonymous
        cookie_id = f"cookie_{uuid.uuid4().hex[:8]}"
        email = f"user_{i}@example.com"
        loyalty_id = f"L_ID_{1000 + i}"
        ip = f"192.168.1.{i % 255}"
        fp = f"fp_{i % 10}"

        # Determine at what point they become known
        become_known_at = random.randint(3, 8)
        become_loyalty_at = random.randint(12, 16)

        for e in range(events_per_user):
            current_identifiers = []
            current_traits = [{"type": "ip", "value": ip}, {"type": "fingerprint", "value": fp}]

            # Stage 1: Anonymous
            current_identifiers.append({"type": "cookie_id", "value": cookie_id})

            # Stage 2: Known (Partial)
            if e >= become_known_at:
                current_identifiers.append({"type": "email", "value": email})

            # Stage 3: Loyalty
            if e >= become_loyalty_at:
                current_identifiers.append({"type": "loyalty_id", "value": loyalty_id})

            event = {
                "identifiers": current_identifiers,
                "traits": current_traits,
                "event": {
                    "event_type": random.choice(event_types),
                    "category": random.choice(categories),
                    "metadata": {"source": "web_portal", "seq": e}
                }
            }
            events.append(event)

    # Add some complex cases (cross-device/merging)
    # Case: User starts on another device (different cookie) but same IP/FP
    for i in range(5):
        ip = f"192.168.1.{i}" # Matches first 5 users
        fp = f"fp_{i}"
        events.append({
            "identifiers": [{"type": "cookie_id", "value": f"tablet_{i}"}],
            "traits": [{"type": "ip", "value": ip}, {"type": "fingerprint", "value": fp}],
            "event": {"event_type": "page_view", "category": "Travel"}
        })

    random.shuffle(events)
    # Limit to roughly 1000 records
    return events[:1000]

if __name__ == "__main__":
    data = generate_data()
    with open("sample_events.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {len(data)} sample records in sample_events.json")
