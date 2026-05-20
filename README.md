# Identity Resolution & Customer Tracking System

A real-time identity resolution engine built with FastAPI and SQLAlchemy. This system tracks customer behavior across different states (unknown, partially known, and loyalty members) and unifies their data into a single canonical profile.

## Features

- **Identity Graph**: Canonical ID mapping with support for multiple identifier types (Email, Phone, Loyalty ID, Cookie ID).
- **Deterministic Matching**: Exact matching on identifiers, with weighted priority for Loyalty IDs.
- **Probabilistic Matching**: Automatic profile linking based on trait overlaps (requires both IP and Browser Fingerprint match).
- **Automatic Profile Merging**: Merges histories, traits, and interest scores when identities are linked.
- **Behavioral Tracking**: Real-time ingestion of customer events (page views, reviews, purchases).
- **Interest Scoring**: Cumulative scoring based on weighted event analysis.
- **Atomic Transactions**: Ensures data integrity with single-commit resolution processes.

## Tech Stack

- **FastAPI**: Modern, high-performance web framework.
- **SQLAlchemy**: Powerful SQL Toolkit and ORM.
- **Gunicorn**: WSGI HTTP Server for production deployment.
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

Start the FastAPI server locally:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. Interactive documentation: `http://127.0.0.1:8000/docs`.

## Testing

### Integration Tests (Pytest)
Run the automated test suite:
```bash
PYTHONPATH=. pytest
```

### End-to-End Testing (Curl)
A helper script `test_api.sh` is provided to simulate a full customer journey.

```bash
# Ensure server is running, then:
chmod +x test_api.sh
./test_api.sh http://127.0.0.1:8000
```

#### Manual Curl Examples
**Track Anonymous Event:**
```bash
curl -X POST "http://127.0.0.1:8000/track" \
     -H "Content-Type: application/json" \
     -d '{
       "identifiers": [{"type": "cookie_id", "value": "anon_123"}],
       "traits": [{"type": "ip", "value": "1.1.1.1"}, {"type": "fingerprint", "value": "fp_123"}],
       "event": {"event_type": "page_view", "category": "Electronics"}
     }'
```

## Interest Scoring Weights

The system calculates interests using the following cumulative weights:
- `purchase`: 5.0
- `customer_review`: 3.0
- `product_view`: 2.0
- `page_view`: 1.0
- `client_event`: 1.0

## Deployment to Google Cloud Platform (GCP)

### Google Cloud Run

1.  **Open Cloud Shell** in the [GCP Console](https://console.cloud.google.com/).
2.  **Clone the code** and enter the directory.
3.  **Deploy**:
    ```bash
    gcloud run deploy id-resolution-api \
      --source . \
      --region us-central1 \
      --allow-unauthenticated
    ```

### Production Considerations
- **Database**: Switch to **Cloud SQL (PostgreSQL)** for production persistence.
- **Environment**: Use GCP Environment Variables to manage `SQLALCHEMY_DATABASE_URL`.
