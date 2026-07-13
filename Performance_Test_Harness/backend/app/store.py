import json
import subprocess
import threading
import time
import uuid
from datetime import datetime, timezone

from . import harness, snowflake_metrics
from .config import resolve_table


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class TestRun:
    def __init__(self, test_id: str, config: dict, table: str, warehouse: str):
        self.test_id = test_id
        self.config = config
        self.table = table
        self.warehouse = warehouse
        self.status = "queued"
        self.created_at = _now()
        self.started_at = None
        self.finished_at = None
        self.error = None
        self.results = None
        self.server_stats = None
        self.server_details = None
        self.cluster_stats = None
        self.cache_stats = None
        self._proc: subprocess.Popen | None = None
        self._stop = threading.Event()

    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "status": self.status,
            "config": self.config,
            "table": self.table,
            "warehouse": self.warehouse,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
            "results": self.results,
            "server_stats": self.server_stats,
            "server_details": self.server_details,
            "cluster_stats": self.cluster_stats,
            "cache_stats": self.cache_stats,
        }


class TestStore:
    def __init__(self) -> None:
        self._runs: dict[str, TestRun] = {}
        self._lock = threading.Lock()

    def get(self, test_id: str) -> TestRun | None:
        return self._runs.get(test_id)

    def list(self) -> list[TestRun]:
        return list(self._runs.values())

    def start(self, config: dict) -> TestRun:
        table_opt = resolve_table(config["table_id"])
        table = table_opt["table"]
        warehouse = table_opt["warehouse"]
        test_id = uuid.uuid4().hex[:12]
        run = TestRun(test_id, config, table, warehouse)
        with self._lock:
            self._runs[test_id] = run
        thread = threading.Thread(target=self._execute, args=(run,), daemon=True)
        thread.start()
        return run

    def stop(self, test_id: str) -> bool:
        run = self._runs.get(test_id)
        if not run or run.status not in ("queued", "running"):
            return False
        run._stop.set()
        if run._proc and run._proc.poll() is None:
            run._proc.terminate()
        run.status = "stopped"
        run.finished_at = _now()
        return True

    def _execute(self, run: TestRun) -> None:
        run.status = "running"
        run.started_at = _now()
        try:
            results = self._run_java(run)
            if run._stop.is_set():
                return
            run.results = results

            # Server-side metrics are best-effort; a missing snowflake connector
            # or transient error must not fail the client-side results.
            self._fetch_metrics(run, results)

            run.status = "completed"
        except Exception as exc:  # noqa: BLE001
            run.status = "error"
            run.error = str(exc)[:1000]
        finally:
            if run.finished_at is None:
                run.finished_at = _now()

    def _run_java(self, run: TestRun) -> dict:
        cmd = harness.build_command(
            table=run.table,
            warehouse=run.warehouse,
            num_connections=run.config["num_connections"],
            duration_seconds=run.config["duration_seconds"],
            query_mix=run.config["query_mix"],
            exec_mode=run.config["exec_mode"],
            ticker_bias=run.config["ticker_bias"],
            result_limit=run.config["result_limit"],
        )
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        run._proc = proc
        timeout = run.config["duration_seconds"] + 120
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            raise RuntimeError("Load test timed out")

        if run._stop.is_set():
            return {}

        if proc.returncode != 0:
            return {
                "latencies": [],
                "query_count": 0,
                "errors": 1,
                "error_messages": [(stderr or "")[:500]],
                "elapsed_total": 0,
                "num_connections": run.config["num_connections"],
                "test_start_ts": _now(),
                "test_end_ts": _now(),
                "conn_timeline": [],
                "unique_tickers": 0,
            }
        return json.loads(stdout)

    def _fetch_metrics(self, run: TestRun, results: dict) -> None:
        if not results or not results.get("test_start_ts"):
            return
        try:
            time.sleep(2)
            stats, details, cluster = snowflake_metrics.fetch_query_history_stats(
                run.warehouse, results["test_start_ts"], results["test_end_ts"]
            )
            run.server_stats = stats
            run.server_details = details
            run.cluster_stats = cluster
        except Exception:
            run.server_stats = run.server_stats or {}

        try:
            run.cache_stats = snowflake_metrics.fetch_cache_stats(
                run.warehouse, results["test_start_ts"], results["test_end_ts"]
            )
        except Exception:
            run.cache_stats = run.cache_stats or {}


store = TestStore()
