import { useEffect, useRef, useState } from "react";
import type {
  ConfigResponse,
  TestConfigRequest,
  TestStatusResponse,
} from "./api/types";
import {
  fetchConfig,
  getApiBaseUrl,
  getTest,
  setApiBaseUrl,
  startTest,
  stopTest,
} from "./api/client";
import { ConfigPanel } from "./components/ConfigPanel";
import { ResultsDashboard } from "./components/ResultsDashboard";
import { Banner } from "./components/ui";

const POLL_INTERVAL_MS = 2000;

export default function App() {
  const [apiUrl, setApiUrl] = useState(getApiBaseUrl());
  const [config, setConfig] = useState<ConfigResponse | null>(null);
  const [form, setForm] = useState<TestConfigRequest | null>(null);
  const [test, setTest] = useState<TestStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingConfig, setLoadingConfig] = useState(false);
  const pollRef = useRef<number | null>(null);

  const running =
    test?.status === "queued" || test?.status === "running";

  async function loadConfig() {
    setLoadingConfig(true);
    setError(null);
    try {
      const cfg = await fetchConfig();
      setConfig(cfg);
      setForm({
        table_id: cfg.defaults.table_id,
        query_mix: cfg.defaults.query_mix,
        exec_mode: cfg.defaults.exec_mode,
        ticker_bias: cfg.defaults.ticker_bias,
        num_connections: cfg.defaults.num_connections,
        duration_seconds: cfg.defaults.duration_seconds,
        result_limit: cfg.defaults.result_limit,
      });
    } catch (e) {
      setError(
        `Could not reach the harness API at ${getApiBaseUrl()}. ${(e as Error).message}`,
      );
    } finally {
      setLoadingConfig(false);
    }
  }

  useEffect(() => {
    loadConfig();
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function beginPolling(testId: string) {
    if (pollRef.current) window.clearInterval(pollRef.current);
    pollRef.current = window.setInterval(async () => {
      try {
        const status = await getTest(testId);
        setTest(status);
        if (
          status.status === "completed" ||
          status.status === "error" ||
          status.status === "stopped"
        ) {
          if (pollRef.current) window.clearInterval(pollRef.current);
          pollRef.current = null;
        }
      } catch (e) {
        setError((e as Error).message);
      }
    }, POLL_INTERVAL_MS);
  }

  async function handleStart() {
    if (!form) return;
    setError(null);
    try {
      const res = await startTest(form);
      const initial = await getTest(res.test_id);
      setTest(initial);
      beginPolling(res.test_id);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function handleStop() {
    if (!test) return;
    try {
      await stopTest(test.test_id);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  function saveApiUrl() {
    setApiBaseUrl(apiUrl);
    loadConfig();
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>RDP Performance Test Harness</h1>
          <p className="subtitle">
            Local frontend for the Snowflake JDBC load-test engine deployed on EC2.
          </p>
        </div>
        <div className="api-config">
          <label>
            Harness API URL
            <div className="api-input-row">
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                placeholder="http://EC2_IP:8000"
              />
              <button className="btn" onClick={saveApiUrl}>
                Connect
              </button>
            </div>
          </label>
        </div>
      </header>

      {error && <Banner kind="error">{error}</Banner>}

      {loadingConfig && !config && <Banner kind="info">Loading configuration...</Banner>}

      {config && form && (
        <div className="layout">
          <aside className="sidebar">
            <ConfigPanel
              config={config}
              value={form}
              onChange={setForm}
              onStart={handleStart}
              onStop={handleStop}
              running={running}
            />
          </aside>
          <main className="main-panel">
            <h2>Performance Results</h2>
            <ResultsDashboard test={test} />
          </main>
        </div>
      )}
    </div>
  );
}
