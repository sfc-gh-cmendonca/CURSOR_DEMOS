# RDP Interactive Tables Performance Test Harness

JDBC load test harness for benchmarking Snowflake standard tables, Interactive Tables, and multi-cluster warehouses against a 36B-row time-series observation workload.

## Architecture

- **Streamlit UI** (`app.py`) — Configuration panel + results dashboard
- **Java JDBC CLI** (`java-harness/src/RdpLoadTest.java`) — Load test engine (called as subprocess)
- **EC2 deployment** (`deploy_to_ec2.sh`) — Automated AWS setup script

### Local frontend + API (alternative to Streamlit)

For driving tests from a laptop while the engine stays on EC2 (close to
Snowflake), there is a client/server split that runs alongside `app.py`:

- **`backend/`** — FastAPI service that wraps the Java engine and Snowflake
  metrics as a REST API. Runs on the EC2 host (port 8000). See `backend/README.md`.
- **`frontend/`** — React + Vite + TypeScript SPA that runs locally and calls the
  EC2 API (URL is configurable). Charts via Recharts. See `frontend/README.md`.

```
[ laptop: React frontend ]  --HTTP-->  [ EC2: FastAPI backend ]  --subprocess-->  [ Java JDBC engine ]  --JDBC-->  [ Snowflake ]
```

Quick start:

```bash
# On EC2 (next to the Java engine, jars, and keys)
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && ./run.sh   # serves :8000

# On your laptop
cd frontend && npm install
echo "VITE_API_BASE_URL=http://<EC2_PUBLIC_IP>:8000" > .env
npm run dev                                    # http://localhost:5173
```

Remember to open port 8000 to your laptop's IP on the EC2 security group (the
same pattern `deploy_to_ec2.sh` uses for 8501).

## Requirements

- Python 3.11+ with `streamlit`, `snowflake-connector-python`, `pandas`
- Java 17+ (Amazon Corretto recommended)
- Snowflake JDBC driver v4.2.0 (`lib/snowflake-jdbc.jar` — download separately)
- SLF4J jars (`lib/slf4j-api.jar`, `lib/slf4j-simple.jar`)
- RSA key pair for Snowflake key-pair auth

## Setup

1. Download JARs into `lib/`:
   ```bash
   mkdir lib
   curl -L -o lib/snowflake-jdbc.jar "https://repo1.maven.org/maven2/net/snowflake/snowflake-jdbc/4.2.0/snowflake-jdbc-4.2.0.jar"
   curl -L -o lib/slf4j-api.jar "https://repo1.maven.org/maven2/org/slf4j/slf4j-api/2.0.9/slf4j-api-2.0.9.jar"
   curl -L -o lib/slf4j-simple.jar "https://repo1.maven.org/maven2/org/slf4j/slf4j-simple/2.0.9/slf4j-simple-2.0.9.jar"
   ```

2. Generate RSA key pair and assign to Snowflake user:
   ```bash
   mkdir keys
   openssl genrsa 2048 | openssl pkcs8 -topk8 -nocrypt -out keys/rsa_key.p8
   openssl rsa -in keys/rsa_key.p8 -pubout -out keys/rsa_key.pub
   # Then in Snowflake: ALTER USER <user> SET RSA_PUBLIC_KEY='<contents of rsa_key.pub without headers>'
   ```

3. Compile Java harness:
   ```bash
   cd java-harness
   javac -cp '../lib/*' -d out src/RdpLoadTest.java
   ```

4. Run locally:
   ```bash
   JAVA_HOME=/path/to/java17 streamlit run app.py --server.port 8501
   ```

## EC2 Deployment

Run `deploy_to_ec2.sh` to provision an m5.4xlarge in eu-central-1 (same region as Snowflake account for minimal latency).

## Configuration Options

- **Target Table:** Standard (1B/5B/36B), Interactive (36B), various clustering strategies
- **Query Mix:** Multi-ticker, single-ticker, date range, TS_CD-based, configurable percentages
- **Connections:** 1-300 concurrent JDBC connections
- **Duration:** 30s-900s
- **Execution Mode:** Sync / Async (8 in-flight per connection)
- **Ticker Distribution:** Uniform / Hot Ticker Bias (80%/50% from top 1000)
- **Result Limit:** No limit / 500 / 1000 / 5000 / 10000 rows
