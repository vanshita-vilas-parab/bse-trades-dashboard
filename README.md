# BSE Trades Dashboard

A full-stack trading dashboard that simulates pulling trades from the Bombay Stock Exchange (BSE) through a delayed mock API.

The application demonstrates how to handle a long-running external API request without blocking the dashboard. Existing trades remain visible while a new trade pull runs in the background, and the UI is automatically updated when the pull completes using Server-Sent Events (SSE).

---

## Problem Statement

The BSE provides a `GET /getTrades` API that can take a long time to respond, with a possible delay of up to 15 minutes.

The dashboard should:

- Open immediately and display previously stored trades.
- Allow the user to start a new trade pull.
- Keep the UI responsive while the BSE request is running.
- Avoid blocking the main API request.
- Automatically display newly received trades when the pull completes.
- Avoid page refreshes.
- Avoid polling.
- Avoid cron jobs or schedulers.

---

## Solution

The application uses a background worker and Server-Sent Events (SSE).

When the user clicks **Pull Latest Trades**:

1. React sends `POST /api/pull` to the Flask backend.
2. Flask immediately starts a background thread.
3. The background thread calls the Mock BSE `/getTrades` API.
4. The Mock BSE API simulates a configurable delay.
5. Existing trades remain available in the dashboard during the pull.
6. Once the BSE response is received, the new trades are stored in SQLite.
7. The backend sends a `pull_completed` SSE event to connected clients.
8. React receives the event and fetches the latest trades.
9. The dashboard updates automatically without a page refresh or polling.

---

## Architecture

```text
                    ┌─────────────────────┐
                    │      React UI        │
                    │    Vite + React      │
                    │      Port 5173       │
                    └──────────┬──────────┘
                               │
                  REST API     │     SSE
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Flask Backend     │
                    │      Port 5000       │
                    └───────┬─────┬───────┘
                            │     │
                  Background│     │ Read trades
                    Thread  │     │
                            ▼     ▼
                  ┌────────────┐ ┌─────────────┐
                  │ Mock BSE   │ │   SQLite    │
                  │ Port 5001  │ │  trades.db  │
                  └────────────┘ └─────────────┘
```

### Pull Flow

```text
User clicks "Pull Latest Trades"
              │
              ▼
       POST /api/pull
              │
              ▼
     Flask starts Thread
              │
              ├──────────────► Immediate response
              │
              ▼
    Mock BSE /getTrades
              │
        Simulated delay
              │
              ▼
      Receive new trades
              │
              ▼
       Save to SQLite
              │
              ▼
      Send SSE event
     "pull_completed"
              │
              ▼
       React receives event
              │
              ▼
       GET /api/trades
              │
              ▼
      Dashboard updates
```

---

## Why Server-Sent Events?

Server-Sent Events (SSE) are used because communication is primarily required in one direction:

**Server → Browser**

The backend needs to tell the React application when the background trade pull has completed.

SSE provides:

- Real-time server-to-client notifications
- A simple HTTP-based implementation
- No polling
- No page refresh
- Less complexity than WebSockets for this use case

---

## Why Background Processing?

The BSE API can take up to 15 minutes to respond.

If the Flask request waited for the BSE API to finish, the `/api/pull` request would remain blocked for the entire duration.

Instead, Flask starts a background thread and immediately responds to the frontend.

This allows:

- The dashboard to remain responsive.
- Existing trades to remain visible.
- The user to see the current pull status.
- The long-running API request to execute independently.

For this assignment, Python's `Thread` is sufficient.

For a production system, a durable background job system such as Celery or RQ with Redis would be more appropriate.

---

## Features

- React-based trading dashboard
- Flask REST API
- Mock BSE API
- SQLite persistence
- Background trade pulling
- Configurable BSE API delay
- Server-Sent Events (SSE)
- Automatic dashboard updates
- Pull status tracking
- Duplicate pull protection
- Responsive UI while trades are being pulled
- No polling
- No page refresh required
- Seeded trade generation
- New trade batches generated on each pull

---

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- HTML
- CSS

### Backend

- Python
- Flask
- Flask-CORS
- Requests
- Server-Sent Events (SSE)
- Python Threading

### Database

- SQLite

### Mock API

- Python
- Flask
- Python-dotenv

---

## Project Structure

```text
bse-trades-dashboard/
│
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── events.py
│   ├── status.py
│   ├── worker.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── mock-bse/
│   ├── app.py
│   ├── seed_data.py
│   ├── trades.json
│   └── requirements.txt
│
├── docs/
│   └── architecture.md
│
├── .gitignore
└── README.md
```

> `.env`, SQLite database files, virtual environments, and `node_modules` are excluded from Git using `.gitignore`.

---

# API Endpoints

## Mock BSE API

### GET `/getTrades`

Returns a new batch of simulated trades after the configured delay.

Example response:

```json
{
  "count": 5000,
  "trades": [
    {
      "tradeId": "TRD00001",
      "client": "Client001",
      "symbol": "RELIANCE",
      "quantity": 100,
      "price": 2450.50,
      "timestamp": "2026-10-09T10:00:00"
    }
  ]
}
```

---

## Backend API

### GET `/api/trades`

Returns all trades currently stored in SQLite.

### POST `/api/pull`

Starts a background trade pull from the Mock BSE API.

The endpoint returns immediately instead of waiting for the BSE request to complete.

If another pull is already running, the backend prevents a duplicate pull.

### GET `/api/status`

Returns the current pull status.

Possible states include:

```text
idle
pulling
completed
failed
```

### GET `/api/events`

Creates an SSE connection between the backend and the React frontend.

The backend sends events such as:

```text
pull_completed
pull_failed
```

---

# Environment Configuration

The Mock BSE API supports a configurable response delay.

Inside `mock-bse/.env`:

```env
BSE_DELAY_SECONDS=10
```

The value `10` is useful during development and demonstrations.

To simulate the maximum 15-minute BSE delay:

```env
BSE_DELAY_SECONDS=900
```

The backend uses:

```env
BSE_API_URL=http://127.0.0.1:5001/getTrades
```

These `.env` files are intentionally excluded from Git.

---

# Installation and Setup

## Prerequisites

Make sure the following are installed:

- Python 3
- Node.js and npm
- Git

---

## 1. Clone the Repository

```bash
git clone https://github.com/vanshita-vilas-parab/bse-trades-dashboard.git
cd bse-trades-dashboard
```

---

# 2. Setup Mock BSE

Open a terminal:

```bash
cd mock-bse
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`:

```env
BSE_DELAY_SECONDS=10
```

Start the Mock BSE API:

```bash
python app.py
```

It will run on:

```text
http://127.0.0.1:5001
```

---

# 3. Setup Backend

Open another terminal:

```bash
cd bse-trades-dashboard/backend
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`:

```env
BSE_API_URL=http://127.0.0.1:5001/getTrades
```

Start Flask:

```bash
python app.py
```

The backend will run on:

```text
http://127.0.0.1:5000
```

SQLite will automatically create the database when the backend starts.

---

# 4. Setup Frontend

Open another terminal:

```bash
cd bse-trades-dashboard/frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will normally run on:

```text
http://localhost:5173
```

Open the displayed URL in your browser.

---

# Running the Complete Application

Three services need to be running:

### Terminal 1 — Mock BSE

```bash
cd mock-bse
source venv/bin/activate
python app.py
```

### Terminal 2 — Backend

```bash
cd backend
source venv/bin/activate
python app.py
```

### Terminal 3 — Frontend

```bash
cd frontend
npm run dev
```

Then open:

```text
http://localhost:5173
```

---

# Testing the Application

### Test 1 — Initial Dashboard

Open the dashboard.

Previously stored trades should appear immediately.

---

### Test 2 — Start a Pull

Click:

```text
Pull Latest Trades
```

The status changes to:

```text
Pulling...
```

The button is disabled while the pull is running.

Existing trades remain visible.

---

### Test 3 — Background Processing

The backend starts the BSE request in a background thread.

The frontend remains responsive while the Mock BSE API is waiting.

---

### Test 4 — Automatic Update

After the configured delay:

1. Mock BSE returns a new batch.
2. Backend saves the trades to SQLite.
3. Backend sends `pull_completed` through SSE.
4. React receives the event.
5. React fetches the latest trades.
6. The dashboard automatically updates.

No page refresh is required.

---

### Test 5 — Multiple Pulls

Each successful pull generates another batch of trades.

For example:

```text
Initial:   5,000 trades
Pull 1:   10,000 trades
Pull 2:   15,000 trades
Pull 3:   20,000 trades
```

Previously stored trades are preserved in SQLite.

---

# Important Design Decisions

## SQLite

SQLite was selected because this is a lightweight assignment and does not require a separate database server.

It provides persistent storage for the pulled trades.

---

## Python Thread

A Python background thread is used to keep the Flask request responsive while waiting for the Mock BSE API.

This is intentionally simple and appropriate for the assignment.

For production workloads, a dedicated job queue such as Celery/RQ with Redis would provide better reliability, retries, monitoring, and scalability.

---

## SSE Instead of Polling

The frontend does not repeatedly ask the backend whether the pull has completed.

Instead, the backend pushes a completion event to the frontend using SSE.

This avoids unnecessary API requests and satisfies the requirement of no polling.

---

## Duplicate Pull Protection

The backend maintains a simple pull status.

If a pull is already running, another `/api/pull` request is rejected instead of starting multiple simultaneous pulls.

---

# Assignment Requirements Mapping

| Requirement | Implementation |
|---|---|
| Mock BSE API | Flask `/getTrades` endpoint |
| Thousands of trades | Mock BSE generates batches of 5,000 trades |
| Configurable delay | `BSE_DELAY_SECONDS` |
| Up to 15-minute delay | `BSE_DELAY_SECONDS=900` |
| Dashboard opens immediately | React loads existing SQLite data |
| Existing trades visible during pull | Data remains in SQLite and dashboard |
| Background processing | Python background thread |
| No page refresh | React updates automatically |
| No polling | SSE event notification |
| Automatic update | `pull_completed` SSE event |
| Persistent storage | SQLite |
| Duplicate pull protection | Backend pull status |
| Architecture documentation | `docs/architecture.md` |
| Video walkthrough | Screen recording with voice-over |

---

# Demo Configuration

For a quick demonstration, use:

```env
BSE_DELAY_SECONDS=10
```

For simulating the assignment's maximum delay:

```env
BSE_DELAY_SECONDS=900
```

The 10-second setting is only for development/demo purposes; the application is designed to support the 15-minute simulated delay.

---

# Future Improvements

For a production-ready implementation, the following improvements could be added:

- Celery/RQ with Redis for durable background jobs
- Job IDs and persistent job status
- Retry handling for failed BSE requests
- Authentication and authorization
- Pagination for large trade datasets
- Database indexing and query optimization
- Production deployment
- Logging and monitoring
- WebSocket/SSE connection management improvements

---

# Author

**Vanshita Vilas Parab**

B.Tech – Information Technology  
AI/ML Honours
