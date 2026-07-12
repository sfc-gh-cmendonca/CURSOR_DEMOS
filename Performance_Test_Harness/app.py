import streamlit as st
import time
import random
import statistics
import json
import subprocess
import pandas as pd
import os
from pathlib import Path
from datetime import datetime, timezone
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import snowflake.connector

st.set_page_config(page_title="RDP Standard Table - JDBC Performance Test Harness", layout="wide")

WAREHOUSE = "RDP_STANDARD_WH"
TABLE = "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION"
TABLE_1B = "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_1B"

SNOWFLAKE_ACCOUNT = "SFSEEUROPE-EU_DEMO59"
SNOWFLAKE_USER = "JACK"
SNOWFLAKE_DATABASE = "THEMES_RESEARCH_DEMO"
SNOWFLAKE_SCHEMA = "RAW_DATA"
PRIVATE_KEY_PATH = str(Path(__file__).parent / "keys" / "rsa_key.p8")


def _load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )
    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


_PRIVATE_KEY_DER = _load_private_key()


def get_connection():
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        account=SNOWFLAKE_ACCOUNT,
        private_key=_PRIVATE_KEY_DER,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        warehouse=WAREHOUSE,
        client_session_keep_alive=True,
        application="RDP_TEST_HARNESS",
    )
    return conn


@st.cache_resource
def get_master_connection():
    return get_connection()


@st.cache_resource
def load_ticker_pool():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT DISTINCT TS_HASH FROM {TABLE} SAMPLE (1000000 ROWS)")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [int(r[0]) for r in rows]
    except Exception as e:
        return []


try:
    TS_HASH_POOL = load_ticker_pool()
except Exception:
    TS_HASH_POOL = []


def generate_multi_ticker_query():
    num_tickers = random.randint(8, min(20, len(TS_HASH_POOL)))
    hashes = random.sample(TS_HASH_POOL, num_tickers)
    hash_list = ", ".join(str(h) for h in hashes)

    query = f"""
SELECT rdp_ts_obsr.TS_CD AS ts_cd, rdp_ts_obsr.DATE_VALUE, rdp_ts_obsr.DATA_VALUE
FROM {TABLE} rdp_ts_obsr
WHERE rdp_ts_obsr.TS_HASH IN ({hash_list})
ORDER BY TS_CD, DATE_VALUE DESC
"""
    return query, hashes


def generate_single_ticker_query():
    ts_hash = random.choice(TS_HASH_POOL)

    query = f"""
SELECT
    TS_HASH,
    TS_CD,
    DATE_VALUE,
    DATA_VALUE,
    DT_LST_UPD
FROM {TABLE}
WHERE DATA_VALUE IS NOT NULL
  AND TS_HASH = {ts_hash}
QUALIFY ROW_NUMBER() OVER(PARTITION BY TS_CD, DATE_VALUE ORDER BY DT_LST_UPD DESC) = 1
ORDER BY 2, 3
"""
    return query, [ts_hash]


def _to_float(val):
    if val is None:
        return 0.0
    return float(str(val))


def fetch_query_history_stats(conn, test_start_ts, test_end_ts):
    cur = conn.cursor()
    cur.execute("USE WAREHOUSE COMPUTE_WH")

    query = f"""
    SELECT
        COUNT(*) AS total_queries,
        COUNT(CASE WHEN EXECUTION_STATUS = 'SUCCESS' THEN 1 END) AS successful_queries,
        COUNT(CASE WHEN EXECUTION_STATUS != 'SUCCESS' THEN 1 END) AS failed_queries,
        MIN(TOTAL_ELAPSED_TIME) AS min_duration_ms,
        MAX(TOTAL_ELAPSED_TIME) AS max_duration_ms,
        AVG(TOTAL_ELAPSED_TIME) AS avg_duration_ms,
        MEDIAN(TOTAL_ELAPSED_TIME) AS median_duration_ms,
        APPROX_PERCENTILE(TOTAL_ELAPSED_TIME, 0.95) AS p95_duration_ms,
        APPROX_PERCENTILE(TOTAL_ELAPSED_TIME, 0.99) AS p99_duration_ms,
        SUM(BYTES_SCANNED) AS total_bytes_scanned,
        AVG(BYTES_SCANNED) AS avg_bytes_scanned,
        SUM(ROWS_PRODUCED) AS total_rows_produced,
        AVG(ROWS_PRODUCED) AS avg_rows_per_query,
        MAX(ROWS_PRODUCED) AS max_rows_per_query,
        AVG(BYTES_WRITTEN_TO_RESULT) AS avg_result_bytes,
        MAX(BYTES_WRITTEN_TO_RESULT) AS max_result_bytes,
        AVG(BYTES_WRITTEN_TO_RESULT / NULLIF(ROWS_PRODUCED, 0)) AS avg_bytes_per_row,
        AVG(COMPILATION_TIME) AS avg_compilation_time_ms,
        AVG(EXECUTION_TIME) AS avg_execution_time_ms,
        MIN(START_TIME) AS first_query_time,
        MAX(END_TIME) AS last_query_time,
        DATEDIFF('millisecond', MIN(START_TIME), MAX(END_TIME)) AS test_window_ms
    FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY_BY_WAREHOUSE(
        WAREHOUSE_NAME => '{WAREHOUSE}',
        END_TIME_RANGE_START => '{test_start_ts}'::TIMESTAMP_LTZ,
        END_TIME_RANGE_END => '{test_end_ts}'::TIMESTAMP_LTZ,
        RESULT_LIMIT => 10000
    ))
    WHERE QUERY_TYPE = 'SELECT'
      AND QUERY_TEXT NOT ILIKE '%USE WAREHOUSE%'
      AND QUERY_TEXT NOT ILIKE '%ALTER SESSION%'
      AND QUERY_TEXT NOT ILIKE '%INFORMATION_SCHEMA%'
    """

    cur.execute(query)
    columns = [desc[0] for desc in cur.description]
    row = cur.fetchone()

    detail_query = f"""
    SELECT
        QUERY_ID,
        TOTAL_ELAPSED_TIME,
        EXECUTION_TIME,
        COMPILATION_TIME,
        BYTES_SCANNED,
        ROWS_PRODUCED,
        EXECUTION_STATUS,
        START_TIME,
        CLUSTER_NUMBER,
        QUEUED_OVERLOAD_TIME
    FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY_BY_WAREHOUSE(
        WAREHOUSE_NAME => '{WAREHOUSE}',
        END_TIME_RANGE_START => '{test_start_ts}'::TIMESTAMP_LTZ,
        END_TIME_RANGE_END => '{test_end_ts}'::TIMESTAMP_LTZ,
        RESULT_LIMIT => 10000
    ))
    WHERE QUERY_TYPE = 'SELECT'
      AND QUERY_TEXT NOT ILIKE '%USE WAREHOUSE%'
      AND QUERY_TEXT NOT ILIKE '%ALTER SESSION%'
      AND QUERY_TEXT NOT ILIKE '%INFORMATION_SCHEMA%'
    ORDER BY START_TIME
    """

    cur.execute(detail_query)
    detail_columns = [desc[0] for desc in cur.description]
    detail_rows = cur.fetchall()

    cluster_query = f"""
    SELECT
        CLUSTER_NUMBER,
        COUNT(*) AS QUERIES_SERVED
    FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY_BY_WAREHOUSE(
        WAREHOUSE_NAME => '{WAREHOUSE}',
        END_TIME_RANGE_START => '{test_start_ts}'::TIMESTAMP_LTZ,
        END_TIME_RANGE_END => '{test_end_ts}'::TIMESTAMP_LTZ,
        RESULT_LIMIT => 10000
    ))
    WHERE QUERY_TYPE = 'SELECT'
      AND QUERY_TEXT NOT ILIKE '%USE WAREHOUSE%'
      AND QUERY_TEXT NOT ILIKE '%ALTER SESSION%'
      AND QUERY_TEXT NOT ILIKE '%INFORMATION_SCHEMA%'
      AND CLUSTER_NUMBER IS NOT NULL
    GROUP BY CLUSTER_NUMBER
    ORDER BY CLUSTER_NUMBER
    """

    cur.execute(cluster_query)
    cluster_columns = [desc[0] for desc in cur.description]
    cluster_rows = cur.fetchall()

    cur.close()

    stats = dict(zip(columns, row)) if row else {}
    details_df = pd.DataFrame(detail_rows, columns=detail_columns) if detail_rows else pd.DataFrame()
    cluster_df = pd.DataFrame(cluster_rows, columns=cluster_columns) if cluster_rows else pd.DataFrame()

    return stats, details_df, cluster_df


def fetch_cache_stats(conn, test_start_ts, test_end_ts):
    cur = conn.cursor()
    cur.execute("USE WAREHOUSE COMPUTE_WH")
    cur.execute("USE ROLE ACCOUNTADMIN")

    cache_query = f"""
    SELECT
        COUNT(*) AS total_queries,
        COUNT(CASE WHEN BYTES_SCANNED = 0 AND EXECUTION_TIME = 0 THEN 1 END) AS result_cache_hits,
        COUNT(CASE WHEN BYTES_SCANNED > 0 AND PERCENTAGE_SCANNED_FROM_CACHE > 0.9 THEN 1 END) AS warehouse_cache_hits,
        COUNT(CASE WHEN BYTES_SCANNED > 0 AND PERCENTAGE_SCANNED_FROM_CACHE <= 0.9 AND PERCENTAGE_SCANNED_FROM_CACHE > 0.1 THEN 1 END) AS partial_cache_hits,
        COUNT(CASE WHEN BYTES_SCANNED > 0 AND PERCENTAGE_SCANNED_FROM_CACHE <= 0.1 THEN 1 END) AS storage_reads,
        AVG(PERCENTAGE_SCANNED_FROM_CACHE) AS avg_pct_from_cache,
        SUM(BYTES_SCANNED) AS total_bytes_scanned,
        SUM(BYTES_SCANNED * PERCENTAGE_SCANNED_FROM_CACHE) AS bytes_from_cache,
        SUM(BYTES_SCANNED * (1 - PERCENTAGE_SCANNED_FROM_CACHE)) AS bytes_from_storage
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
    WHERE WAREHOUSE_NAME = '{WAREHOUSE}'
      AND QUERY_TYPE = 'SELECT'
      AND START_TIME >= '{test_start_ts}'::TIMESTAMP_LTZ
      AND END_TIME <= '{test_end_ts}'::TIMESTAMP_LTZ
      AND QUERY_TEXT NOT ILIKE '%USE WAREHOUSE%'
      AND QUERY_TEXT NOT ILIKE '%ALTER SESSION%'
      AND QUERY_TEXT NOT ILIKE '%INFORMATION_SCHEMA%'
      AND QUERY_TEXT NOT ILIKE '%ACCOUNT_USAGE%'
    """

    cur.execute(cache_query)
    columns = [desc[0] for desc in cur.description]
    row = cur.fetchone()
    cur.execute("USE ROLE SYSADMIN")
    cur.close()

    return dict(zip(columns, row)) if row else {}


import json
import subprocess


JAVA_HARNESS_DIR = str(Path(__file__).parent / "java-harness")
JDBC_JAR_PATH = str(Path(__file__).parent / "lib" / "snowflake-jdbc.jar")
SLF4J_API_JAR = str(Path(__file__).parent / "lib" / "slf4j-api.jar")
SLF4J_SIMPLE_JAR = str(Path(__file__).parent / "lib" / "slf4j-simple.jar")


def run_load_test(duration_seconds, num_connections, query_mix, exec_mode="sync", ticker_bias="uniform", result_limit="0"):
    mix_map = {
        "Mixed (60% multi-ticker, 40% single-ticker)": "mixed",
        "Multi-ticker lookup only": "multi",
        "Single-ticker deduplicated only": "single",
        "Multi-ticker with date range": "multi_date",
        "Single-ticker mix (80% single, 20% single+date range)": "single_date_mix",
        "Single-ticker mix (50% single, 50% single+date range)": "single_date_50",
        "Single-ticker with date range only (100%)": "single_date_100",
        "TS_CD single lookup": "tscd_single",
        "TS_CD with date range": "tscd_date",
        "TS_CD multi-ticker lookup": "tscd_multi",
        "TS_CD mixed (50% single, 30% date, 20% multi)": "tscd_mixed",
        "Full mix (40% multi, 30% multi+date, 30% single)": "full_mix",
    }
    mix_arg = mix_map.get(query_mix, "mixed")

    java_home = os.environ.get("JAVA_HOME", "/usr/lib/jvm/java-17-amazon-corretto.x86_64")
    java_bin = os.path.join(java_home, "bin", "java")

    cmd = [
        java_bin,
        "--add-opens=java.base/java.nio=ALL-UNNAMED",
        "-cp",
        os.path.join(JAVA_HARNESS_DIR, "out") + ":" + JDBC_JAR_PATH + ":" + SLF4J_API_JAR + ":" + SLF4J_SIMPLE_JAR,
        "RdpLoadTest",
        "--warehouse", WAREHOUSE,
        "--table", TABLE,
        "--user", SNOWFLAKE_USER,
        "--account", SNOWFLAKE_ACCOUNT,
        "--database", SNOWFLAKE_DATABASE,
        "--schema", SNOWFLAKE_SCHEMA,
        "--key", PRIVATE_KEY_PATH,
        "--connections", str(num_connections),
        "--duration", str(duration_seconds),
        "--rampup", str(min(30, duration_seconds // 2)),
        "--mix", mix_arg,
        "--mode", exec_mode,
        "--ticker_bias", ticker_bias,
        "--result_limit", result_limit,
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=duration_seconds + 120)

    if proc.returncode != 0:
        return {
            "latencies": [],
            "query_count": 0,
            "errors": 1,
            "error_messages": [proc.stderr[:500]],
            "elapsed_total": 0,
            "num_connections": num_connections,
            "test_start_ts": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "test_end_ts": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "conn_timeline": [],
            "unique_tickers": 0,
        }

    results = json.loads(proc.stdout)
    return results


st.title("RDP Standard Table - JDBC Performance Test Harness")
st.markdown(
    f"Simulate **diverse user queries** via **Snowflake JDBC connector** against "
    f"**Standard Table** (`{TABLE}`) served by **Multi-Cluster Warehouse** (`{WAREHOUSE}` — Small, 5-15 clusters)."
)

st.divider()

col_config, col_results = st.columns([1, 2])

with col_config:
    st.subheader("Test Configuration")

    target_table = st.selectbox(
        "Target Table",
        [
            "RDP_TIMESERIES_OBSERVATION (36B rows)",
            "RDP_TIMESERIES_OBSERVATION_IT (36B rows - Interactive)",
            "RDP_TIMESERIES_OBSERVATION_IT_DATE_SO (36B rows - Interactive, DATE cluster + SO on TS_CD)",
            "RDP_TIMESERIES_OBSERVATION_IT_TSCD (36B rows - Interactive, Ordered by TS_CD + SO)",
            "RDP_TIMESERIES_OBSERVATION_36B_V2 (36B rows - 8-level TS_CD)",
            "RDP_TIMESERIES_OBSERVATION_36B_V2_ORDERED (36B rows - Ordered + SO)",
            "RDP_TIMESERIES_OBSERVATION_36B_V2_ORDERED_NOCLUSTER (36B rows - Ordered + SO, No AC)",
            "RDP_TIMESERIES_OBSERVATION_36B_SPLIT (36B rows - Clustered on TS_CD)",
            "RDP_TIMESERIES_OBSERVATION_5B_SPLIT (5B rows - Clustered on TS_CD)",
            "RDP_TIMESERIES_OBSERVATION_1B (1B rows)",
            "RDP_TIMESERIES_OBSERVATION_1B_SPLIT (1B rows - Clustered on TS_CD)",
        ]
    )
    if "IT_TSCD" in target_table:
        TABLE = "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_IT_TSCD"
        WAREHOUSE = "RDP_INTERACTIVE_WH"
    elif "IT_DATE_SO" in target_table:
        TABLE = "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_IT_DATE_SO"
        WAREHOUSE = "RDP_INTERACTIVE_WH"
    elif "Interactive" in target_table:
        TABLE = "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_IT"
        WAREHOUSE = "RDP_INTERACTIVE_WH"
    elif "36B_V2_ORDERED_NOCLUSTER" in target_table:
        TABLE = "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_36B_V2_ORDERED_NOCLUSTER"
        WAREHOUSE = "RDP_STANDARD_WH"
    elif "36B_V2_ORDERED" in target_table:
        TABLE = "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_36B_V2_ORDERED"
        WAREHOUSE = "RDP_STANDARD_WH"
    elif "36B_V2" in target_table:
        TABLE = "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_36B_V2"
        WAREHOUSE = "RDP_STANDARD_WH"
    elif "36B_SPLIT" in target_table:
        TABLE = "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_36B_SPLIT"
        WAREHOUSE = "RDP_STANDARD_WH"
    elif "5B_SPLIT" in target_table:
        TABLE = "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_5B_SPLIT"
        WAREHOUSE = "RDP_STANDARD_WH"
    elif "1B_SPLIT" in target_table:
        TABLE = "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_1B_SPLIT"
        WAREHOUSE = "RDP_STANDARD_WH"
    elif "36B" in target_table:
        TABLE = "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION"
        WAREHOUSE = "RDP_STANDARD_WH"
    else:
        TABLE = "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_1B"
        WAREHOUSE = "RDP_STANDARD_WH"

    try:
        _conn = get_master_connection()
        _cur = _conn.cursor()
        _cur.execute(f"SELECT SYSTEM$CLUSTERING_INFORMATION('{TABLE}')")
        import json as _json
        _ci = _json.loads(_cur.fetchone()[0])
        _depth = _ci.get("average_depth", "N/A")
        _overlaps = _ci.get("average_overlaps", "N/A")
        _key = _ci.get("cluster_by_keys", "N/A")
        _cur.close()
        st.markdown(f"**Clustering:** `{_key}` — Depth: **{_depth:.2f}**, Overlaps: **{_overlaps:.2f}**")
    except Exception:
        pass

    query_mix = st.selectbox(
        "Query Mix",
        ["Single-ticker deduplicated only", "Single-ticker with date range only (100%)", "Single-ticker mix (80% single, 20% single+date range)", "Single-ticker mix (50% single, 50% single+date range)", "Multi-ticker lookup only", "Multi-ticker with date range", "Mixed (60% multi-ticker, 40% single-ticker)", "Full mix (40% multi, 30% multi+date, 30% single)", "TS_CD single lookup", "TS_CD with date range", "TS_CD multi-ticker lookup", "TS_CD mixed (50% single, 30% date, 20% multi)"]
    )

    exec_mode = st.selectbox(
        "Execution Mode",
        ["Sync (Default)", "Async (8 in-flight per connection)"]
    )

    ticker_bias = st.selectbox(
        "Ticker Distribution",
        ["Uniform (random from 1M pool)", "Hot Ticker Bias 80% (from top 1,000)", "Hot Ticker Bias 50% (from top 1,000)"],
        help="Hot bias simulates popular tickers being queried more frequently — improves warehouse cache hit rate"
    )

    num_connections = st.slider(
        "Concurrent JDBC Connections",
        min_value=1, max_value=300, value=100, step=1,
        help="Each simulated user gets its own JDBC connection (replicating RDP team setup)"
    )

    duration = st.slider("Test Duration (seconds)", min_value=5, max_value=900, value=120, step=5)

    result_limit = st.selectbox(
        "Result Limit (rows per query)",
        ["No limit (full result set)", "500 rows", "1000 rows", "5000 rows", "10000 rows"],
        help="Limit rows returned per query to reduce client-side transfer overhead"
    )
    limit_map = {"No limit (full result set)": "0", "500 rows": "500", "1000 rows": "1000", "5000 rows": "5000", "10000 rows": "10000"}
    limit_arg = limit_map.get(result_limit, "0")

    if st.button("🔄 Refresh Ticker Pool", help="Load a new random sample of 10,000 tickers from the 15M available"):
        load_ticker_pool.clear()
        st.rerun()

    with st.expander("Query Templates"):
        st.markdown("**Multi-ticker lookup** — randomly selects 3-10 tickers per query:")
        st.code(generate_multi_ticker_query()[0], language="sql")
        st.markdown("**Single-ticker deduplicated** — randomly selects 1 ticker:")
        st.code(generate_single_ticker_query()[0], language="sql")

    st.info(
        f"**{num_connections} JDBC connections** each send randomized queries with different ticker "
        f"combinations from a pool of **{len(TS_HASH_POOL)} tickers** — simulating diverse user traffic. "
        f"Driver: Snowflake JDBC (Java). Result cache enabled."
    )

    if "test_running" not in st.session_state:
        st.session_state.test_running = False
    if "test_results" not in st.session_state:
        st.session_state.test_results = None
    if "sf_stats" not in st.session_state:
        st.session_state.sf_stats = None
    if "sf_details" not in st.session_state:
        st.session_state.sf_details = None
    if "sf_cluster" not in st.session_state:
        st.session_state.sf_cluster = None
    if "sf_cache" not in st.session_state:
        st.session_state.sf_cache = None

    col_start, col_stop = st.columns(2)

    with col_start:
        start_btn = st.button("Start Test", type="primary", disabled=st.session_state.test_running)

    with col_stop:
        stop_btn = st.button("Stop Test", disabled=not st.session_state.test_running)

    if start_btn and not st.session_state.test_running:
        st.session_state.test_running = True
        st.session_state.test_results = None
        st.session_state.sf_stats = None
        st.session_state.sf_details = None
        st.session_state.sf_cluster = None
        st.session_state.sf_cache = None

        with st.spinner(f"Running JDBC load test: {num_connections} connections × {duration}s on {WAREHOUSE}..."):
            bias_arg = "uniform"
            if "80%" in ticker_bias:
                bias_arg = "hot80"
            elif "50%" in ticker_bias:
                bias_arg = "hot50"
            results = run_load_test(duration, num_connections, query_mix, "async" if "Async" in exec_mode else "sync", bias_arg, limit_arg)

        st.session_state.test_results = results
        st.session_state.test_running = False

        with st.spinner("Fetching server-side metrics from INFORMATION_SCHEMA..."):
            time.sleep(2)
            master_conn = get_master_connection()
            sf_stats, sf_details, sf_cluster = fetch_query_history_stats(
                master_conn, results["test_start_ts"], results["test_end_ts"]
            )
            st.session_state.sf_stats = sf_stats
            st.session_state.sf_details = sf_details
            st.session_state.sf_cluster = sf_cluster

        with st.spinner("Fetching cache metrics from ACCOUNT_USAGE (may be empty if <45min old)..."):
            cache_stats = fetch_cache_stats(
                master_conn, results["test_start_ts"], results["test_end_ts"]
            )
            st.session_state.sf_cache = cache_stats

        st.rerun()

    if stop_btn and st.session_state.test_running:
        st.session_state.test_running = False
        st.rerun()

with col_results:
    st.subheader("Performance Results")

    if st.session_state.test_results:
        results = st.session_state.test_results
        latencies = results["latencies"]
        query_count = results["query_count"]
        errors = results["errors"]
        elapsed_total = results["elapsed_total"]
        num_conns = results.get("num_connections", 1)

        if latencies:
            avg_latency = statistics.mean(latencies)
            p50_latency = statistics.median(latencies)
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else latencies[0]
            p99_latency = sorted(latencies)[int(len(latencies) * 0.99)] if len(latencies) > 1 else latencies[0]
            min_latency = min(latencies)
            max_latency = max(latencies)
            qps = query_count / elapsed_total if elapsed_total > 0 else 0

            st.success(
                f"Test completed: **{query_count}** unique queries across **{num_conns} JDBC connections** "
                f"in **{elapsed_total:.1f}s**"
            )

            m1, m2, m3, m4, m5, m6 = st.columns(6)
            m1.metric("Queries/sec (QPS)", f"{qps:.2f}")
            m2.metric("Total Queries", f"{query_count}")
            m3.metric("Errors", f"{errors}")
            m4.metric("JDBC Connections", f"{num_conns}")
            m5.metric("Unique Tickers", f"{results.get('unique_tickers', 0):,}")
            m6.metric("Avg Rows/Query", f"{results.get('avg_rows_per_query', 0):,.0f}")

            st.divider()
            st.markdown("##### Result Transfer Details")

            avg_rows_client = results.get("avg_rows_per_query", 0)
            max_rows_client = results.get("max_rows_per_query", 0)
            r1, r2, r3 = st.columns(3)
            r1.metric("Avg Rows / Query", f"{avg_rows_client:,.0f}")
            r2.metric("Max Rows / Query", f"{max_rows_client:,}")
            r3.metric("CLIENT_RESULT_CHUNK_SIZE", "16 MB")

            chunks_1 = results.get("chunks_1", 0)
            chunks_2 = results.get("chunks_2", 0)
            chunks_3plus = results.get("chunks_3plus", 0)
            ch1, ch2, ch3 = st.columns(3)
            ch1.metric("1 Chunk", f"{chunks_1:,}")
            ch2.metric("2 Chunks", f"{chunks_2:,}")
            ch3.metric("3+ Chunks", f"{chunks_3plus:,}")

            st.divider()
            st.markdown("##### JDBC Session Parameters (from server)")
            sp1, sp2 = st.columns(2)
            v1_api = results.get("session_v1_query_api", "unknown")
            prefetch = results.get("session_prefetch_threads", "unknown")
            api_label = "V1" if v1_api in ("true", "True") else "V2" if v1_api in ("false", "False") else v1_api
            sp1.metric("Query API Version", api_label)
            sp2.metric("Prefetch Threads", prefetch)

            st.divider()
            st.markdown("##### Client-Side Latency (end-to-end incl. network)")

            l1, l2, l3 = st.columns(3)
            l1.metric("Avg Latency", f"{avg_latency*1000:.1f} ms")
            l2.metric("P50 (Median)", f"{p50_latency*1000:.1f} ms")
            l3.metric("P95", f"{p95_latency*1000:.1f} ms")

            l4, l5, l6 = st.columns(3)
            l4.metric("P99", f"{p99_latency*1000:.1f} ms")
            l5.metric("Min", f"{min_latency*1000:.1f} ms")
            l6.metric("Max", f"{max_latency*1000:.1f} ms")

            sf_stats = st.session_state.sf_stats
            sf_details = st.session_state.sf_details

            if sf_stats and sf_stats.get("TOTAL_QUERIES"):
                st.divider()
                sampled = int(_to_float(sf_stats['TOTAL_QUERIES']))
                sample_note = f" (sampled {sampled:,} of {query_count:,})" if sampled < query_count else ""
                st.markdown(f"##### Server-Side Metrics (from INFORMATION_SCHEMA){sample_note}")

                s1, s2, s3 = st.columns(3)
                s1.metric("Queries Served", f"{query_count:,}")
                s2.metric("Successful", f"{sf_stats['SUCCESSFUL_QUERIES']}")
                s3.metric("Failed", f"{sf_stats['FAILED_QUERIES']}")

                test_window_s = _to_float(sf_stats["TEST_WINDOW_MS"]) / 1000 if sf_stats["TEST_WINDOW_MS"] else elapsed_total
                throughput = query_count / test_window_s if test_window_s > 0 else 0

                t1, t2, t3 = st.columns(3)
                t1.metric("Throughput (QPS)", f"{throughput:.2f}")
                t2.metric("Avg Compilation", f"{_to_float(sf_stats['AVG_COMPILATION_TIME_MS']):.1f} ms")
                t3.metric("Avg Execution", f"{_to_float(sf_stats['AVG_EXECUTION_TIME_MS']):.1f} ms")

                st.markdown("##### Server-Side Duration (TOTAL_ELAPSED_TIME)")

                d1, d2, d3 = st.columns(3)
                d1.metric("Min Duration", f"{_to_float(sf_stats['MIN_DURATION_MS']):.0f} ms")
                d2.metric("Avg Duration", f"{_to_float(sf_stats['AVG_DURATION_MS']):.1f} ms")
                d3.metric("Max Duration", f"{_to_float(sf_stats['MAX_DURATION_MS']):.0f} ms")

                d4, d5, d6 = st.columns(3)
                d4.metric("Median (P50)", f"{_to_float(sf_stats['MEDIAN_DURATION_MS']):.1f} ms")
                d5.metric("P95 Duration", f"{_to_float(sf_stats['P95_DURATION_MS']):.1f} ms")
                d6.metric("P99 Duration", f"{_to_float(sf_stats['P99_DURATION_MS']):.1f} ms")

                bytes_scanned_mb = _to_float(sf_stats["TOTAL_BYTES_SCANNED"]) / (1024 * 1024)
                rows_produced = _to_float(sf_stats["TOTAL_ROWS_PRODUCED"])
                avg_rows_per_query = _to_float(sf_stats["AVG_ROWS_PER_QUERY"])
                max_rows_per_query = _to_float(sf_stats["MAX_ROWS_PER_QUERY"])
                avg_result_kb = _to_float(sf_stats["AVG_RESULT_BYTES"]) / 1024
                max_result_kb = _to_float(sf_stats["MAX_RESULT_BYTES"]) / 1024
                avg_bytes_per_row = _to_float(sf_stats["AVG_BYTES_PER_ROW"])

                b1, b2, b3 = st.columns(3)
                b1.metric("Total Bytes Scanned", f"{bytes_scanned_mb:.2f} MB")
                b2.metric("Total Rows Produced", f"{rows_produced:,.0f}")
                b3.metric("Avg Bytes / Row", f"{avg_bytes_per_row:.1f}")

                b4, b5, b6 = st.columns(3)
                b4.metric("Avg Rows / Query", f"{avg_rows_per_query:,.0f}")
                b5.metric("Max Rows / Query", f"{max_rows_per_query:,.0f}")
                b6.metric("Avg Result Size", f"{avg_result_kb:.1f} KB")

                b7, b8 = st.columns(2)
                b7.metric("Max Result Size", f"{max_result_kb:.1f} KB")
                b8.metric("Result vs Chunk Limit", f"{avg_result_kb / (16 * 1024) * 100:.2f}%", help="Avg result as % of CLIENT_RESULT_CHUNK_SIZE (16MB)")

                if sf_details is not None and not sf_details.empty:
                    st.divider()
                    st.markdown("##### Server-Side Latency Over Time")
                    chart_df = sf_details[["START_TIME", "TOTAL_ELAPSED_TIME"]].copy()
                    chart_df = chart_df.rename(columns={"TOTAL_ELAPSED_TIME": "Duration (ms)"})
                    chart_df = chart_df.reset_index(drop=True)
                    chart_df["Query #"] = range(1, len(chart_df) + 1)
                    st.line_chart(chart_df, x="Query #", y="Duration (ms)")

                    st.markdown("##### Server-Side Latency Histogram")
                    server_hist_data = chart_df["Duration (ms)"].value_counts(bins=20).sort_index()
                    server_hist_df = pd.DataFrame({
                        "Latency (ms)": [f"{int(interval.left)}-{int(interval.right)}" for interval in server_hist_data.index],
                        "Count": server_hist_data.values
                    })
                    st.bar_chart(server_hist_df, x="Latency (ms)", y="Count")

                    st.markdown("##### Compilation vs Execution Time")
                    breakdown_df = sf_details[["COMPILATION_TIME", "EXECUTION_TIME"]].copy()
                    breakdown_df["Query #"] = range(1, len(breakdown_df) + 1)
                    st.line_chart(breakdown_df, x="Query #", y=["COMPILATION_TIME", "EXECUTION_TIME"])

                    st.markdown("##### Queue Time (Overload)")
                    queue_df = sf_details[["QUEUED_OVERLOAD_TIME"]].copy()
                    queue_df["Query #"] = range(1, len(queue_df) + 1)
                    queue_df = queue_df.rename(columns={"QUEUED_OVERLOAD_TIME": "Queue Time (ms)"})
                    st.line_chart(queue_df, x="Query #", y="Queue Time (ms)")

                    queued_count = (sf_details["QUEUED_OVERLOAD_TIME"] > 0).sum()
                    avg_queue = sf_details["QUEUED_OVERLOAD_TIME"].mean()
                    max_queue = sf_details["QUEUED_OVERLOAD_TIME"].max()
                    q1, q2, q3 = st.columns(3)
                    q1.metric("Queries Queued", f"{queued_count} ({queued_count/len(sf_details)*100:.1f}%)")
                    q2.metric("Avg Queue Time", f"{avg_queue:.1f} ms")
                    q3.metric("Max Queue Time", f"{max_queue:.0f} ms")

                sf_cluster = st.session_state.sf_cluster
                has_cluster_data = False

                if sf_cluster is not None and not sf_cluster.empty:
                    has_cluster_data = True
                    st.divider()
                    st.markdown("##### Queries Served per Cluster")
                    cluster_chart = sf_cluster.copy()
                    cluster_chart["CLUSTER_NUMBER"] = cluster_chart["CLUSTER_NUMBER"].astype(int).astype(str)
                    cluster_chart = cluster_chart.rename(columns={"CLUSTER_NUMBER": "Cluster", "QUERIES_SERVED": "Queries"})
                    st.bar_chart(cluster_chart, x="Cluster", y="Queries")
                elif sf_details is not None and not sf_details.empty and "CLUSTER_NUMBER" in sf_details.columns:
                    cluster_data = sf_details[sf_details["CLUSTER_NUMBER"].notna()].groupby("CLUSTER_NUMBER").size().reset_index(name="QUERIES_SERVED")
                    if not cluster_data.empty:
                        has_cluster_data = True
                        st.divider()
                        st.markdown("##### Queries Served per Cluster")
                        cluster_chart = cluster_data.copy()
                        cluster_chart["CLUSTER_NUMBER"] = cluster_chart["CLUSTER_NUMBER"].astype(int).astype(str)
                        cluster_chart = cluster_chart.rename(columns={"CLUSTER_NUMBER": "Cluster", "QUERIES_SERVED": "Queries"})
                        st.bar_chart(cluster_chart, x="Cluster", y="Queries")

                if not has_cluster_data:
                    st.divider()
                    st.info("All queries served from result cache (no cluster assignment).")

                sf_cache = st.session_state.sf_cache
                if sf_cache and sf_cache.get("TOTAL_QUERIES") and sf_cache["TOTAL_QUERIES"] > 0:
                    st.divider()
                    st.markdown("##### Cache Performance (from ACCOUNT_USAGE)")

                    total_q = sf_cache["TOTAL_QUERIES"]
                    result_cache_pct = (sf_cache["RESULT_CACHE_HITS"] / total_q * 100) if total_q else 0
                    wh_cache_pct = (sf_cache["WAREHOUSE_CACHE_HITS"] / total_q * 100) if total_q else 0
                    partial_pct = (sf_cache["PARTIAL_CACHE_HITS"] / total_q * 100) if total_q else 0
                    storage_pct = (sf_cache["STORAGE_READS"] / total_q * 100) if total_q else 0
                    avg_cache_pct = (sf_cache["AVG_PCT_FROM_CACHE"] or 0) * 100

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Result Cache", f"{result_cache_pct:.1f}%", help="Queries served entirely from result cache (0 bytes scanned)")
                    c2.metric("Warehouse Cache", f"{wh_cache_pct:.1f}%", help="Queries where >90% of data read from local SSD cache")
                    c3.metric("Partial Cache", f"{partial_pct:.1f}%", help="Queries with 10-90% data from cache")
                    c4.metric("Remote Storage", f"{storage_pct:.1f}%", help="Queries where >90% of data read from remote storage")

                    st.metric("Avg % Scanned from Warehouse Cache", f"{avg_cache_pct:.1f}%")

                    total_bytes = sf_cache["TOTAL_BYTES_SCANNED"] or 0
                    bytes_cache = sf_cache["BYTES_FROM_CACHE"] or 0
                    bytes_storage = sf_cache["BYTES_FROM_STORAGE"] or 0
                    if total_bytes > 0:
                        cache_df = pd.DataFrame({
                            "Source": ["Warehouse Cache", "Remote Storage"],
                            "Bytes (MB)": [bytes_cache / (1024*1024), bytes_storage / (1024*1024)]
                        })
                        st.bar_chart(cache_df, x="Source", y="Bytes (MB)")
                elif sf_cache is not None and (not sf_cache.get("TOTAL_QUERIES") or sf_cache["TOTAL_QUERIES"] == 0):
                    st.divider()
                    st.info(
                        "⏳ Cache metrics not yet available — ACCOUNT_USAGE has ~45 min latency. "
                        "Re-open the app after 45 minutes to see cache breakdown for this test run."
                    )

            elif sf_stats is not None:
                st.divider()
                st.warning(
                    "No queries found in INFORMATION_SCHEMA for this test window. "
                    "This can happen if queries haven't propagated yet. "
                    "Try re-running with a longer duration."
                )

            st.divider()
            st.markdown("##### Active JDBC Connections Over Time")

            conn_timeline = results.get("conn_timeline", [])
            if conn_timeline:
                conn_df = pd.DataFrame(conn_timeline, columns=["Time (s)", "Active Connections"])
                st.line_chart(conn_df, x="Time (s)", y="Active Connections")

            st.divider()
            st.markdown("##### Client-Side Latency Over Time")

            df_latency = pd.DataFrame({
                "Query #": range(1, len(latencies) + 1),
                "Latency (ms)": [l * 1000 for l in latencies]
            })
            st.line_chart(df_latency, x="Query #", y="Latency (ms)")

            st.markdown("##### Client-Side Latency Histogram")
            hist_data = df_latency["Latency (ms)"].value_counts(bins=20).sort_index()
            hist_df = pd.DataFrame({
                "Latency (ms)": [f"{int(interval.left)}-{int(interval.right)}" for interval in hist_data.index],
                "Count": hist_data.values
            })
            st.bar_chart(hist_df, x="Latency (ms)", y="Count")

            if errors > 0 and results["error_messages"]:
                st.divider()
                st.markdown("##### Errors")
                for msg in results["error_messages"]:
                    st.error(msg)
        else:
            st.warning("No queries completed during the test run.")
    else:
        st.info("Configure and start a test run to see performance results here.")

st.divider()
st.caption(
    f"Table: `{TABLE}` | "
    f"Warehouse: `{WAREHOUSE}` (Small, 5-15 clusters) | "
    f"Driver: Snowflake JDBC (Java) | "
    f"Ticker Pool: {len(TS_HASH_POOL)}"
)
