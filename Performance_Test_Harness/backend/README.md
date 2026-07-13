# Harness API (FastAPI)

HTTP API that wraps the Java JDBC load-test engine and Snowflake metrics so a
remote frontend (running on your laptop) can drive tests on this host.

This is intended to run **on the EC2 instance** (see `../deploy_to_ec2.sh`),
co-located with Snowflake for low latency, exactly where the Java engine and the
RSA key already live. The original Streamlit `app.py` is unchanged and can still
be used independently.

## Endpoints

| Method | Path                     | Description                                  |
| ------ | ------------------------ | -------------------------------------------- |
| GET    | `/api/health`            | Liveness probe                               |
| GET    | `/api/config`            | Available tables, query mixes, defaults      |
| POST   | `/api/tests`             | Start a load test (returns `test_id`)        |
| GET    | `/api/tests/{id}`        | Poll status + client/server-side results     |
| POST   | `/api/tests/{id}/stop`   | Best-effort stop of a running test           |
| GET    | `/api/tests`             | List known test runs                         |

Interactive docs are served at `/docs`.

## Requirements

Same runtime prerequisites as `app.py`:

- Python 3.11+
- Java 17+ with the compiled engine in `../java-harness/out`
- `../lib/snowflake-jdbc.jar`, `../lib/slf4j-*.jar`
- `../keys/rsa_key.p8` (Snowflake key-pair auth)

## Run

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional: copy and edit environment overrides
cp .env.example .env   # then `export $(grep -v '^#' .env | xargs)`

./run.sh               # serves on 0.0.0.0:8000
```

## Configuration

All settings have sensible defaults (matching `app.py`) and can be overridden via
environment variables. See `.env.example`. Set `CORS_ORIGINS` to the origin your
laptop frontend is served from (default allows Vite's `http://localhost:5173`).

## Notes

- A test runs the Java engine as a subprocess in a background thread; poll
  `GET /api/tests/{id}` until `status` is `completed` / `error` / `stopped`.
- Server-side metrics (`INFORMATION_SCHEMA`) and cache metrics (`ACCOUNT_USAGE`,
  ~45 min latency) are fetched best-effort and will be `null`/empty if the
  Snowflake connector is unavailable or the data has not propagated yet.
- State is in-memory (single instance); restarting the server clears run history.
