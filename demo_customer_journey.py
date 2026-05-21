import json
import httpx
import time

BASE_URL = "http://127.0.0.1:8000"

def track(identifiers, traits=None, event=None):
    payload = {
        "identifiers": identifiers,
        "traits": traits or [],
        "event": event
    }
    resp = httpx.post(f"{BASE_URL}/track", json=payload)
    return resp.json()

def get_profile(id_type, id_value):
    resp = httpx.get(f"{BASE_URL}/profile/{id_type}/{id_value}")
    return resp.json()

def run_story():
    print("=== IDENTITY RESOLUTION STORY: THE CUSTOMER JOURNEY ===\n")

    # PERSONA 1: Alice - The Fashion Enthusiast
    # Phase 1: Anonymous on Mobile
    print("--- Alice Phase 1: Anonymous browsing on Mobile ---")
    res = track(
        identifiers=[{"type": "cookie_id", "value": "alice_mobile_cookie"}],
        traits=[{"type": "ip", "value": "1.1.1.1"}, {"type": "fingerprint", "value": "ios_v1"}],
        event={"event_type": "page_view", "category": "Fashion"}
    )
    print(f"Profile Created: {res['canonical_id']} | Interests: {[s['category'] for s in res['interest_scores']]}")

    # Phase 2: Sign up with Email
    print("\n--- Alice Phase 2: Signs up with Email ---")
    res = track(
        identifiers=[
            {"type": "cookie_id", "value": "alice_mobile_cookie"},
            {"type": "email", "value": "alice@example.com"}
        ],
        event={"event_type": "product_view", "category": "Fashion"}
    )
    print(f"Profile Linked: {res['canonical_id']} | Identifiers: {[i['type'] + ':' + i['value'] for i in res['identifiers']]}")

    # Phase 3: Joins Loyalty Program
    print("\n--- Alice Phase 3: Joins Loyalty Program ---")
    res = track(
        identifiers=[
            {"type": "email", "value": "alice@example.com"},
            {"type": "loyalty_id", "value": "L_ALICE_001"}
        ],
        event={"event_type": "purchase", "category": "Fashion"}
    )
    print(f"Stitched to Loyalty: {res['canonical_id']} | Total Fashion Score: {next(s['score'] for s in res['interest_scores'] if s['category'] == 'Fashion')}")

    print("\n" + "="*50 + "\n")

    # PERSONA 2: Bob - The Multi-Device Techie
    # Phase 1: Anonymous on Desktop
    print("--- Bob Phase 1: Anonymous on Desktop (Electronics) ---")
    res_desktop = track(
        identifiers=[{"type": "cookie_id", "value": "bob_desktop_cookie"}],
        event={"event_type": "page_view", "category": "Electronics"}
    )
    print(f"Profile 1 (Desktop): {res_desktop['canonical_id']}")

    # Phase 2: Anonymous on Laptop (Same IP/FP)
    print("\n--- Bob Phase 2: Anonymous on Laptop (Same IP/FP) ---")
    res_laptop = track(
        identifiers=[{"type": "cookie_id", "value": "bob_laptop_cookie"}],
        traits=[{"type": "ip", "value": "2.2.2.2"}, {"type": "fingerprint", "value": "mac_v99"}],
        event={"event_type": "page_view", "category": "Electronics"}
    )
    # We need to set traits for desktop too for probabilistic to work
    track(
        identifiers=[{"type": "cookie_id", "value": "bob_desktop_cookie"}],
        traits=[{"type": "ip", "value": "2.2.2.2"}, {"type": "fingerprint", "value": "mac_v99"}]
    )

    # Phase 3: Probabilistic Merge
    print("\n--- Bob Phase 3: Re-tracking Laptop (Now Probabilistic Merge should trigger) ---")
    res_merged = track(
        identifiers=[{"type": "cookie_id", "value": "bob_laptop_cookie"}],
        traits=[{"type": "ip", "value": "2.2.2.2"}, {"type": "fingerprint", "value": "mac_v99"}],
        event={"event_type": "product_view", "category": "Electronics"}
    )
    print(f"Merged Profile: {res_merged['canonical_id']} | Cookies: {[i['value'] for i in res_merged['identifiers'] if i['type'] == 'cookie_id']}")

    # Phase 4: Consolidate with Loyalty
    print("\n--- Bob Phase 4: Logs in with Loyalty ID ---")
    res_final = track(
        identifiers=[
            {"type": "loyalty_id", "value": "L_BOB_999"},
            {"type": "cookie_id", "value": "bob_desktop_cookie"}
        ],
        event={"event_type": "purchase", "category": "Electronics"}
    )
    print(f"Final Loyalty Profile: {res_final['canonical_id']}")
    print(f"Consolidated Interests: {[(s['category'], s['score']) for s in res_final['interest_scores']]}")

    print("\n=== STORY COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    try:
        run_story()
    except Exception as e:
        print(f"Error: {e}. Is the server running at {BASE_URL}?")
