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
