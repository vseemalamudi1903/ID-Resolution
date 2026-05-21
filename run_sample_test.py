import json
import httpx
import time
import sys

def run_test(base_url="http://127.0.0.1:8000"):
    print(f"Starting Identity Resolution Demo against {base_url}...")

    try:
        with open("sample_events.json", "r") as f:
            events = json.load(f)
    except FileNotFoundError:
        print("Error: sample_events.json not found. Run generate_sample_data.py first.")
        return

    # Track distinct profiles we see to show progress
    seen_canonical_ids = set()

    start_time = time.time()
    processed_count = 0

    print(f"{'Seq':<5} | {'Identifiers':<40} | {'Canonical ID':<40} | {'Status'}")
    print("-" * 100)

    for i, event_data in enumerate(events):
        try:
            response = httpx.post(f"{base_url}/track", json=event_data, timeout=10.0)
            if response.status_code == 200:
                result = response.json()
                can_id = result["canonical_id"]

                status = "NEW"
                if can_id in seen_canonical_ids:
                    status = "EXISTING"
                else:
                    seen_canonical_ids.add(can_id)

                # Show every 50th record or interesting merges
                if i % 50 == 0 or len(event_data["identifiers"]) > 1:
                    ids_str = ", ".join([f"{d['type']}:{d['value']}" for d in event_data["identifiers"]])
                    print(f"{i:<5} | {ids_str[:38]:<40} | {can_id:<40} | {status}")

                processed_count += 1
            else:
                print(f"Error at seq {i}: {response.status_code}")
        except Exception as e:
            print(f"Request failed at seq {i}: {str(e)}")
            break

    duration = time.time() - start_time
    print("-" * 100)
    print(f"Demo Completed!")
    print(f"Total events processed: {processed_count}")
    print(f"Unique canonical profiles resolved: {len(seen_canonical_ids)}")
    print(f"Total time: {duration:.2f} seconds")

    # Sample a detailed profile at the end
    if seen_canonical_ids:
        # We need to find an identifier to query the GET /profile endpoint
        # Let's just grab the last successful result's first identifier
        last_event = events[-1]
        id_type = last_event["identifiers"][0]["type"]
        id_value = last_event["identifiers"][0]["value"]

        print(f"\nFetching detailed profile via identifier {id_type}:{id_value}...")
        try:
            resp = httpx.get(f"{base_url}/profile/{id_type}/{id_value}")
            if resp.status_code == 200:
                print(json.dumps(resp.json(), indent=2))
            else:
                print(f"Failed to fetch profile: {resp.status_code}")
        except Exception as e:
            print(f"Error fetching profile: {str(e)}")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    run_test(url)
