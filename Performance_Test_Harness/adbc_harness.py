"""
ADBC (Arrow Database Connectivity) load test harness for Snowflake.

Returns results natively as Arrow RecordBatches — no JDBC chunk downloads,
no JVM, no serialization overhead. Drop-in replacement for the Java JDBC CLI.
"""

import time
import random
import threading
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import adbc_driver_snowflake.dbapi as adbc_snowflake


def run_adbc_test(config: dict) -> dict:
    """Run load test using ADBC Snowflake driver. Returns same JSON schema as Java CLI."""

    account = config["account"]
    user = config["user"]
    database = config["database"]
    schema = config["schema"]
    warehouse = config["warehouse"]
    table = config["table"]
    key_path = config["key_path"]
    num_connections = config["connections"]
    duration_seconds = config["duration"]
    rampup_seconds = config.get("rampup", min(30, duration_seconds // 2))
    query_mix = config["mix"]
    ticker_bias = config.get("ticker_bias", "uniform")
    result_limit = config.get("result_limit", 0)

    # Build DSN URI with key-pair auth (no MFA needed)
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    import base64

    with open(key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
    pk_der = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    pk_b64 = base64.urlsafe_b64encode(pk_der).decode('utf-8')

    dsn = f'{user}@{account}/{database}/{schema}?warehouse={warehouse}&authenticator=SNOWFLAKE_JWT&privateKey={pk_b64}'

    pool_wh = 'RDP_STANDARD_WH' if '_IT' in table else warehouse
    pool_dsn = f'{user}@{account}/{database}/{schema}?warehouse={pool_wh}&authenticator=SNOWFLAKE_JWT&privateKey={pk_b64}'

    # Load ticker pools using Python connector (more reliable for warehouse resume)
    ts_hash_pool, ts_cd_pool = _load_pools_python(config, table, query_mix)

    hot_pool = ts_hash_pool[:1000] if len(ts_hash_pool) >= 1000 else ts_hash_pool

    # Shared state
    all_latencies = []
    all_errors = []
    all_row_counts = []
    all_tickers = set()
    conn_timeline = []
    active_connections = [0]
    lock = threading.Lock()

    test_start = time.time()
    test_start_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    stop_event = threading.Event()

    def worker(worker_id):
        nonlocal active_connections
        latencies = []
        errors = 0
        error_msgs = []
        row_counts = []
        tickers_used = set()
        rng = random.Random(worker_id * 31 + int(time.time()))

        try:
            conn = adbc_snowflake.connect(dsn)
            cur = conn.cursor()
            cur.execute("ALTER SESSION SET USE_CACHED_RESULT = TRUE")
        except Exception as e:
            with lock:
                all_errors.append(str(e)[:200])
            return

        with lock:
            active_connections[0] += 1
            conn_timeline.append((time.time(), active_connections[0]))

        try:
            end_time = test_start + duration_seconds
            while time.time() < end_time and not stop_event.is_set():
                sql, used_tickers = _generate_query(
                    rng, query_mix, table, ts_hash_pool, hot_pool, ts_cd_pool,
                    ticker_bias, result_limit
                )
                tickers_used.update(used_tickers)

                start = time.time()
                try:
                    cur.execute(sql)
                    reader = cur.fetch_record_batch()
                    n_rows = 0
                    for batch in reader:
                        n_rows += batch.num_rows
                    elapsed_ms = (time.time() - start) * 1000
                    latencies.append(elapsed_ms)
                    row_counts.append(n_rows)
                except Exception as e:
                    errors += 1
                    error_msgs.append(str(e)[:200])
        finally:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass
            with lock:
                active_connections[0] -= 1
                conn_timeline.append((time.time(), active_connections[0]))
                all_latencies.extend(latencies)
                all_errors.extend(error_msgs)
                all_row_counts.extend(row_counts)
                all_tickers.update(tickers_used)

    # Ramp up workers
    futures = []
    with ThreadPoolExecutor(max_workers=num_connections) as executor:
        delay_per_worker = rampup_seconds / max(num_connections, 1)
        for i in range(num_connections):
            if i > 0 and delay_per_worker > 0:
                time.sleep(delay_per_worker)
            futures.append(executor.submit(worker, i))

        for f in as_completed(futures):
            pass  # wait for all workers

    test_end = time.time()
    test_end_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    elapsed_total = test_end - test_start

    avg_rows = sum(all_row_counts) / len(all_row_counts) if all_row_counts else 0
    max_rows = max(all_row_counts) if all_row_counts else 0

    # Format conn_timeline relative to start
    formatted_timeline = [[round(t - test_start, 3), c] for t, c in conn_timeline]

    return {
        "query_count": len(all_latencies),
        "errors": len(all_errors),
        "elapsed_total": round(elapsed_total, 2),
        "num_connections": num_connections,
        "unique_tickers": len(all_tickers),
        "avg_rows_per_query": round(avg_rows, 1),
        "max_rows_per_query": max_rows,
        "chunks_1": len(all_latencies),  # ADBC = always 1 "chunk" (inline Arrow)
        "chunks_2": 0,
        "chunks_3plus": 0,
        "test_start_ts": test_start_ts,
        "test_end_ts": test_end_ts,
        "latencies": [round(l / 1000, 6) for l in all_latencies],
        "conn_timeline": formatted_timeline,
        "error_messages": all_errors[:10],
        "session_v1_query_api": "N/A (ADBC)",
        "session_prefetch_threads": "N/A (ADBC)",
    }


def _load_pools_python(config, table, query_mix):
    """Load ticker pools using Python connector (handles warehouse resume reliably)."""
    import snowflake.connector

    pool_wh = 'RDP_STANDARD_WH' if '_IT' in table else config["warehouse"]
    pool_table = table if '_IT' not in table else "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION"

    conn = snowflake.connector.connect(
        account=config["account"],
        user=config["user"],
        private_key=config["private_key_der"],
        database=config["database"],
        schema=config["schema"],
        warehouse=pool_wh,
    )
    cur = conn.cursor()

    ts_hash_pool = []
    ts_cd_pool = []
    is_tscd = query_mix.startswith("tscd_")

    if is_tscd:
        cur.execute(f"SELECT DISTINCT TS_CD FROM {pool_table} SAMPLE (100000 ROWS)")
        ts_cd_pool = [row[0] for row in cur.fetchall()]
    else:
        cur.execute(f"SELECT DISTINCT TS_HASH FROM {pool_table} SAMPLE (100000 ROWS)")
        ts_hash_pool = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()
    return ts_hash_pool, ts_cd_pool


def _load_pools(dsn, table, query_mix):
    """Load ticker hash and/or TS_CD pools."""
    ts_hash_pool = []
    ts_cd_pool = []

    is_tscd = query_mix.startswith("tscd_")
    pool_table = table if not ("_IT" in table) else "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION"

    try:
        conn = adbc_snowflake.connect(dsn)
        cur = conn.cursor()

        if is_tscd:
            cur.execute(f"SELECT DISTINCT TS_CD FROM {pool_table} TABLESAMPLE (0.01) LIMIT 10000")
            ts_cd_pool = [row[0] for row in cur.fetchall()]
        else:
            cur.execute(f"SELECT DISTINCT TS_HASH FROM {pool_table} TABLESAMPLE (0.01) LIMIT 10000")
            ts_hash_pool = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()
    except Exception as e:
        raise RuntimeError(f"Failed to load ticker pool: {e}")

    return ts_hash_pool, ts_cd_pool


def _generate_query(rng, mix, table, hash_pool, hot_pool, cd_pool, bias, limit):
    """Generate a random query based on mix type. Returns (sql, set_of_tickers_used)."""

    def apply_limit(sql):
        if limit and int(limit) > 0:
            return sql + f" LIMIT {limit}"
        return sql

    def pick_hash():
        if bias == "hot80" and rng.random() < 0.8 and hot_pool:
            return rng.choice(hot_pool)
        elif bias == "hot50" and rng.random() < 0.5 and hot_pool:
            return rng.choice(hot_pool)
        return rng.choice(hash_pool)

    def pick_cd():
        return rng.choice(cd_pool)

    def date_range():
        start_year = 2020 + rng.randint(0, 3)
        start_month = rng.randint(1, 12)
        start_date = f"{start_year}-{start_month:02d}-01"
        range_months = rng.randint(6, 24)
        end_year = start_year + (start_month + range_months - 1) // 12
        end_month = (start_month + range_months - 1) % 12 + 1
        end_date = f"{end_year}-{end_month:02d}-28"
        return start_date, end_date

    # TS_CD-based queries
    if mix == "tscd_single":
        cd = pick_cd()
        sql = f"SELECT TS_CD, DATE_VALUE, DATA_VALUE FROM {table} WHERE TS_CD = '{cd}' ORDER BY DATE_VALUE DESC"
        return apply_limit(sql), {cd}

    elif mix == "tscd_date":
        cd = pick_cd()
        sd, ed = date_range()
        sql = (f"SELECT TS_CD, DATE_VALUE, DATA_VALUE FROM {table} "
               f"WHERE TS_CD = '{cd}' AND DATE_VALUE BETWEEN '{sd}' AND '{ed}' ORDER BY DATE_VALUE DESC")
        return apply_limit(sql), {cd}

    elif mix == "tscd_multi":
        num = rng.randint(5, 10)
        cds = set()
        while len(cds) < num:
            cds.add(pick_cd())
        in_clause = ",".join(f"'{c}'" for c in cds)
        sql = f"SELECT TS_CD, DATE_VALUE, DATA_VALUE FROM {table} WHERE TS_CD IN ({in_clause}) ORDER BY TS_CD, DATE_VALUE DESC"
        return apply_limit(sql), cds

    elif mix == "tscd_mixed":
        r = rng.random()
        if r < 0.5:
            return _generate_query(rng, "tscd_single", table, hash_pool, hot_pool, cd_pool, bias, limit)
        elif r < 0.8:
            return _generate_query(rng, "tscd_date", table, hash_pool, hot_pool, cd_pool, bias, limit)
        else:
            return _generate_query(rng, "tscd_multi", table, hash_pool, hot_pool, cd_pool, bias, limit)

    # TS_HASH-based queries
    elif mix == "multi":
        num = rng.randint(8, min(20, len(hash_pool)))
        hashes = set()
        while len(hashes) < num:
            hashes.add(pick_hash())
        in_clause = ",".join(str(h) for h in hashes)
        sql = f"SELECT TS_CD, DATE_VALUE, DATA_VALUE FROM {table} WHERE TS_HASH IN ({in_clause}) ORDER BY TS_CD, DATE_VALUE DESC"
        return apply_limit(sql), hashes

    elif mix == "single":
        h = pick_hash()
        sql = (f"SELECT TS_HASH, TS_CD, DATE_VALUE, DATA_VALUE, DT_LST_UPD FROM {table} "
               f"WHERE DATA_VALUE IS NOT NULL AND TS_HASH = {h} "
               f"QUALIFY ROW_NUMBER() OVER(PARTITION BY TS_CD, DATE_VALUE ORDER BY DT_LST_UPD DESC) = 1 "
               f"ORDER BY 2, 3")
        return apply_limit(sql), {h}

    elif mix == "multi_date":
        num = rng.randint(8, min(20, len(hash_pool)))
        hashes = set()
        while len(hashes) < num:
            hashes.add(pick_hash())
        sd, ed = date_range()
        in_clause = ",".join(str(h) for h in hashes)
        sql = (f"SELECT TS_CD, DATE_VALUE, DATA_VALUE FROM {table} "
               f"WHERE TS_HASH IN ({in_clause}) AND DATE_VALUE BETWEEN '{sd}' AND '{ed}' "
               f"ORDER BY TS_CD, DATE_VALUE DESC")
        return apply_limit(sql), hashes

    elif mix in ("single_date_mix", "single_date_50", "single_date_100"):
        threshold = 0.2 if mix == "single_date_mix" else 0.5 if mix == "single_date_50" else 1.0
        if rng.random() < threshold:
            h = pick_hash()
            sd, ed = date_range()
            sql = (f"SELECT TS_CD, DATE_VALUE, DATA_VALUE FROM {table} "
                   f"WHERE TS_HASH = {h} AND DATE_VALUE BETWEEN '{sd}' AND '{ed}' ORDER BY DATE_VALUE DESC")
            return apply_limit(sql), {h}
        else:
            return _generate_query(rng, "single", table, hash_pool, hot_pool, cd_pool, bias, limit)

    elif mix == "full_mix":
        r = rng.random()
        if r < 0.4:
            return _generate_query(rng, "multi", table, hash_pool, hot_pool, cd_pool, bias, limit)
        elif r < 0.7:
            return _generate_query(rng, "multi_date", table, hash_pool, hot_pool, cd_pool, bias, limit)
        else:
            return _generate_query(rng, "single", table, hash_pool, hot_pool, cd_pool, bias, limit)

    else:  # "mixed" default
        if rng.random() < 0.6:
            return _generate_query(rng, "multi", table, hash_pool, hot_pool, cd_pool, bias, limit)
        else:
            return _generate_query(rng, "single", table, hash_pool, hot_pool, cd_pool, bias, limit)
