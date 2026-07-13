# Harness Frontend (React + Vite + TypeScript)

A local web UI for the RDP Performance Test Harness. It runs on your laptop and
talks to the harness API (`../backend`) deployed on EC2, replacing the need to
open the Streamlit UI over the network.

Charts are rendered with [Recharts](https://recharts.org/).

## Prerequisites

- Node.js 18+ and npm
- A reachable harness API (the FastAPI backend running on EC2, port 8000)

## Setup

```bash
cd frontend
npm install

# Point the app at your EC2 harness API
cp .env.example .env
# edit .env -> VITE_API_BASE_URL=http://YOUR_EC2_PUBLIC_IP:8000
```

The API URL can also be changed at runtime from the header field in the app; it
is persisted to `localStorage`.

## Develop

```bash
npm run dev        # http://localhost:5173
```

## Build

```bash
npm run build      # type-checks then bundles to dist/
npm run preview    # serve the production build locally
```

## How it connects

1. On load, the app calls `GET /api/config` to populate the configuration panel.
2. **Start Test** issues `POST /api/tests`, then polls `GET /api/tests/{id}`
   every 2s until the run completes.
3. Client-side latency stats are computed in the browser from the returned
   `latencies`; server-side and cache metrics are rendered from the API payload.

## CORS

The backend must allow this app's origin. If you serve the frontend from a port
other than `5173`, set `CORS_ORIGINS` on the backend accordingly.
