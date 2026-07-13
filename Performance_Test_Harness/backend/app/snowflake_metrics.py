from datetime import date, datetime
from decimal import Decimal

from .config import settings

_PRIVATE_KEY_DER = None


def _load_private_key():
    global _PRIVATE_KEY_DER
    if _PRIVATE_KEY_DER is not None:
        return _PRIVATE_KEY_DER
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    with open(settings.private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )
    _PRIVATE_KEY_DER = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return _PRIVATE_KEY_DER


def _get_connection(warehouse: str):
    import snowflake.connector

    return snowflake.connector.connect(
        user=settings.snowflake_user,
        account=settings.snowflake_account,
        private_key=_load_private_key(),
        database=settings.snowflake_database,
        schema=settings.snowflake_schema,
        warehouse=warehouse,
        client_session_keep_alive=True,
        application="RDP_TEST_HARNESS_API",
    )


def _jsonable(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _rows_to_dicts(columns, rows):
    return [{c: _jsonable(v) for c, v in zip(columns, row)} for row in rows]


def fetch_query_history_stats(warehouse: str, test_start_ts: str, test_end_ts: str):
    """Server-side metrics from INFORMATION_SCHEMA. Returns (stats, details, cluster)."""
    conn = _get_connection(warehouse)
    try:
        cur = conn.cursor()
        cur.execute(f"USE WAREHOUSE {settings.metrics_warehouse}")

        summary_query = f"""
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
            WAREHOUSE_NAME => '{warehouse}',
            END_TIME_RANGE_START => '{test_start_ts}'::TIMESTAMP_LTZ,
            END_TIME_RANGE_END => '{test_end_ts}'::TIMESTAMP_LTZ,
            RESULT_LIMIT => 10000
        ))
        WHERE QUERY_TYPE = 'SELECT'
          AND QUERY_TEXT NOT ILIKE '%USE WAREHOUSE%'
          AND QUERY_TEXT NOT ILIKE '%ALTER SESSION%'
          AND QUERY_TEXT NOT ILIKE '%INFORMATION_SCHEMA%'
        """
        cur.execute(summary_query)
        columns = [d[0] for d in cur.description]
        row = cur.fetchone()
        stats = {c: _jsonable(v) for c, v in zip(columns, row)} if row else {}

        detail_query = f"""
        SELECT
            QUERY_ID, TOTAL_ELAPSED_TIME, EXECUTION_TIME, COMPILATION_TIME,
            BYTES_SCANNED, ROWS_PRODUCED, EXECUTION_STATUS, START_TIME,
            CLUSTER_NUMBER, QUEUED_OVERLOAD_TIME
        FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY_BY_WAREHOUSE(
            WAREHOUSE_NAME => '{warehouse}',
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
        detail_columns = [d[0] for d in cur.description]
        details = _rows_to_dicts(detail_columns, cur.fetchall())

        cluster_query = f"""
        SELECT CLUSTER_NUMBER, COUNT(*) AS QUERIES_SERVED
        FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY_BY_WAREHOUSE(
            WAREHOUSE_NAME => '{warehouse}',
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
        cluster_columns = [d[0] for d in cur.description]
        cluster = _rows_to_dicts(cluster_columns, cur.fetchall())

        cur.close()
        return stats, details, cluster
    finally:
        conn.close()


def fetch_cache_stats(warehouse: str, test_start_ts: str, test_end_ts: str):
    """Cache breakdown from ACCOUNT_USAGE (has ~45 min latency)."""
    conn = _get_connection(warehouse)
    try:
        cur = conn.cursor()
        cur.execute(f"USE WAREHOUSE {settings.metrics_warehouse}")
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
        WHERE WAREHOUSE_NAME = '{warehouse}'
          AND QUERY_TYPE = 'SELECT'
          AND START_TIME >= '{test_start_ts}'::TIMESTAMP_LTZ
          AND END_TIME <= '{test_end_ts}'::TIMESTAMP_LTZ
          AND QUERY_TEXT NOT ILIKE '%USE WAREHOUSE%'
          AND QUERY_TEXT NOT ILIKE '%ALTER SESSION%'
          AND QUERY_TEXT NOT ILIKE '%INFORMATION_SCHEMA%'
          AND QUERY_TEXT NOT ILIKE '%ACCOUNT_USAGE%'
        """
        cur.execute(cache_query)
        columns = [d[0] for d in cur.description]
        row = cur.fetchone()
        try:
            cur.execute("USE ROLE SYSADMIN")
        except Exception:
            pass
        cur.close()
        return {c: _jsonable(v) for c, v in zip(columns, row)} if row else {}
    finally:
        conn.close()
