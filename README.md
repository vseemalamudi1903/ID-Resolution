# Identity Resolution & Customer Tracking System

A real-time identity resolution engine built with FastAPI and SQLAlchemy. This system tracks customer behavior across different states (unknown, partially known, and loyalty members) and unifies their data into a single canonical profile.

## Features

- **Identity Graph**: Canonical ID mapping with support for multiple identifier types (Email, Phone, Loyalty ID, Cookie ID).
- **Deterministic Matching**: Exact matching on identifiers, with weighted priority for Loyalty IDs.
- **Probabilistic Matching**: Automatic profile linking based on trait overlaps (requiring both IP and Browser Fingerprint match).
- **Automatic Profile Merging**: Merges histories, traits, and interest scores when identities are linked.
- **Behavioral Tracking**: Real-time ingestion of customer events (page views, reviews, purchases).
- **Interest Scoring**: Cumulative scoring based on weighted event analysis.
- **Atomic Transactions**: Ensures data integrity with single-commit resolution processes.

## Tech Stack

- **FastAPI**: Modern, high-performance web framework.
- **SQLAlchemy**: Powerful SQL Toolkit and ORM.
- **SQLite**: Local database for development and testing.
- **Pytest**: For comprehensive integration testing.

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. You can access the interactive documentation at `http://127.0.0.1:8000/docs`.

### Running Tests

Run the integration test suite:
```bash
PYTHONPATH=. pytest
```

## API Usage Examples

### 1. Track an Anonymous Event
Ingest a page view from an anonymous user with a cookie and browser traits.

```bash
curl -X POST "http://127.0.0.1:8000/track" \
     -H "Content-Type: application/json" \
     -d '{
       "identifiers": [{"type": "cookie_id", "value": "anon_123"}],
       "traits": [{"type": "ip", "value": "192.168.1.1"}, {"type": "fingerprint", "value": "browser_x"}],
       "event": {"event_type": "page_view", "category": "Electronics"}
     }'
```

### 2. Link to an Email (Partial Knowledge)
When the user provides an email, the system will link it to the existing anonymous profile.

```bash
curl -X POST "http://127.0.0.1:8000/track" \
     -H "Content-Type: application/json" \
     -d '{
       "identifiers": [
         {"type": "cookie_id", "value": "anon_123"},
         {"type": "email", "value": "john@example.com"}
       ],
       "event": {"event_type": "product_view", "category": "Electronics"}
     }'
```

### 3. Retrieve a Unified Profile
Get the full canonical view of a customer using any of their identifiers.

```bash
curl "http://127.0.0.1:8000/profile/email/john@example.com"
```

## Interest Scoring Weights

The system automatically calculates interest scores using the following weights:
- `purchase`: 5.0
- `customer_review`: 3.0
- `product_view`: 2.0
- `page_view`: 1.0
- `client_event`: 1.0

## Testing with `curl`

You can test the identity resolution logic using the provided `test_api.sh` script or by running manual commands.

### Using the Test Script

This script simulates a full customer journey: Anonymous -> Known (Email) -> Loyalty.

1.  **Ensure the server is running** (either locally or on GCP).
2.  **Run the script**:
    ```bash
    # For local testing
    ./test_api.sh http://127.0.0.1:8000

    # For GCP testing
    ./test_api.sh https://your-cloud-run-url.a.run.app
    ```
    *Note: The script requires `jq` for pretty-printing JSON.*

### Manual Command Examples

#### 1. Track an Anonymous Event
Ingest a page view from an anonymous user.
```bash
curl -X POST "http://127.0.0.1:8000/track" \
     -H "Content-Type: application/json" \
     -d '{
       "identifiers": [{"type": "cookie_id", "value": "anon_123"}],
       "traits": [{"type": "ip", "value": "1.1.1.1"}, {"type": "fingerprint", "value": "fp_123"}],
       "event": {"event_type": "page_view", "category": "Electronics"}
     }'
```

#### 2. Link Email to anonymous profile
```bash
curl -X POST "http://127.0.0.1:8000/track" \
     -H "Content-Type: application/json" \
     -d '{
       "identifiers": [
         {"type": "cookie_id", "value": "anon_123"},
         {"type": "email", "value": "john@example.com"}
       ],
       "event": {"event_type": "product_view", "category": "Electronics"}
     }'
```

#### 3. Retrieve Profile
```bash
curl "http://127.0.0.1:8000/profile/email/john@example.com"
```

## Deployment to Google Cloud Platform (GCP)

You can deploy this application to **Google Cloud Run** directly from the Cloud Console.

### Step-by-Step Guide

1.  **Open Cloud Shell**: Click the "Activate Cloud Shell" button in the top right of the [GCP Console](https://console.cloud.google.com/).
2.  **Clone/Upload Code**: Clone this repository into your Cloud Shell environment.
    ```bash
    git clone <your-repo-url>
    cd ID-Resolution
    ```
3.  **Build and Deploy with Cloud Run**:
    Run the following command to build the container image and deploy it:
    ```bash
    gcloud run deploy id-resolution-api \
      --source . \
      --region us-central1 \
      --allow-unauthenticated \
      --platform managed
    ```
    *Note: GCP will automatically use the included `Dockerfile` to build the image via Cloud Build.*

4.  **Verify Deployment**:
    Once the command finishes, it will provide a Service URL (e.g., `https://id-resolution-api-xxxxx.a.run.app`). You can test the `/health` endpoint or use the interactive `/docs` UI.

### Production Considerations for GCP
- **Database**: The current implementation uses local SQLite. For production on GCP, switch to **Cloud SQL (PostgreSQL)** by updating the `SQLALCHEMY_DATABASE_URL` in `app/database.py` and using environment variables.
- **Persistence**: Cloud Run is stateless. Files stored on the container (like `id_resolution.db`) will be lost when the instance scales down.
