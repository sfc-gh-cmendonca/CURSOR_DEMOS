import json
import os
import subprocess
from datetime import datetime, timezone

from .config import settings


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def build_command(table: str, warehouse: str, num_connections: int,
                  duration_seconds: int, query_mix: str, exec_mode: str,
                  ticker_bias: str, result_limit: str) -> list[str]:
    java_bin = os.path.join(settings.java_home, "bin", "java")
    classpath = ":".join([
        os.path.join(settings.java_harness_dir, "out"),
        settings.jdbc_jar_path,
        settings.slf4j_api_jar,
        settings.slf4j_simple_jar,
    ])
    return [
        java_bin,
        "--add-opens=java.base/java.nio=ALL-UNNAMED",
        "-cp", classpath,
        "RdpLoadTest",
        "--warehouse", warehouse,
        "--table", table,
        "--user", settings.snowflake_user,
        "--account", settings.snowflake_account,
        "--database", settings.snowflake_database,
        "--schema", settings.snowflake_schema,
        "--key", settings.private_key_path,
        "--connections", str(num_connections),
        "--duration", str(duration_seconds),
        "--rampup", str(min(30, duration_seconds // 2)),
        "--mix", query_mix,
        "--mode", exec_mode,
        "--ticker_bias", ticker_bias,
        "--result_limit", result_limit,
    ]


def run_load_test(table: str, warehouse: str, num_connections: int,
                  duration_seconds: int, query_mix: str, exec_mode: str,
                  ticker_bias: str, result_limit: str) -> dict:
    """Run the Java JDBC load-test engine as a subprocess and parse its JSON.

    Mirrors run_load_test() from the original Streamlit app.py.
    """
    cmd = build_command(
        table, warehouse, num_connections, duration_seconds,
        query_mix, exec_mode, ticker_bias, result_limit,
    )

    proc = subprocess.run(
        cmd, capture_output=True, text=True, timeout=duration_seconds + 120
    )

    if proc.returncode != 0:
        return {
            "latencies": [],
            "query_count": 0,
            "errors": 1,
            "error_messages": [proc.stderr[:500]],
            "elapsed_total": 0,
            "num_connections": num_connections,
            "test_start_ts": _now_utc(),
            "test_end_ts": _now_utc(),
            "conn_timeline": [],
            "unique_tickers": 0,
        }

    return json.loads(proc.stdout)
