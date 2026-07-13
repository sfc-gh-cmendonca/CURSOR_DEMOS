import type { ConfigResponse, TestConfigRequest } from "../api/types";

interface Props {
  config: ConfigResponse;
  value: TestConfigRequest;
  onChange: (value: TestConfigRequest) => void;
  onStart: () => void;
  onStop: () => void;
  running: boolean;
}

export function ConfigPanel({
  config,
  value,
  onChange,
  onStart,
  onStop,
  running,
}: Props) {
  const set = <K extends keyof TestConfigRequest>(
    key: K,
    v: TestConfigRequest[K],
  ) => onChange({ ...value, [key]: v });

  const selectedTable = config.tables.find((t) => t.id === value.table_id);

  return (
    <div className="config-panel">
      <h2>Test Configuration</h2>

      <label className="field">
        <span>Target Table</span>
        <select
          value={value.table_id}
          disabled={running}
          onChange={(e) => set("table_id", e.target.value)}
        >
          {config.tables.map((t) => (
            <option key={t.id} value={t.id}>
              {t.label}
            </option>
          ))}
        </select>
      </label>

      {selectedTable && (
        <p className="hint">
          Warehouse: <code>{selectedTable.warehouse}</code>
        </p>
      )}

      <label className="field">
        <span>Query Mix</span>
        <select
          value={value.query_mix}
          disabled={running}
          onChange={(e) => set("query_mix", e.target.value)}
        >
          {config.query_mixes.map((o) => (
            <option key={o.id} value={o.id}>
              {o.label}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Execution Mode</span>
        <select
          value={value.exec_mode}
          disabled={running}
          onChange={(e) => set("exec_mode", e.target.value)}
        >
          {config.exec_modes.map((o) => (
            <option key={o.id} value={o.id}>
              {o.label}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Ticker Distribution</span>
        <select
          value={value.ticker_bias}
          disabled={running}
          onChange={(e) => set("ticker_bias", e.target.value)}
        >
          {config.ticker_biases.map((o) => (
            <option key={o.id} value={o.id}>
              {o.label}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Concurrent JDBC Connections: {value.num_connections}</span>
        <input
          type="range"
          min={1}
          max={300}
          step={1}
          value={value.num_connections}
          disabled={running}
          onChange={(e) => set("num_connections", Number(e.target.value))}
        />
      </label>

      <label className="field">
        <span>Test Duration (seconds): {value.duration_seconds}</span>
        <input
          type="range"
          min={5}
          max={900}
          step={5}
          value={value.duration_seconds}
          disabled={running}
          onChange={(e) => set("duration_seconds", Number(e.target.value))}
        />
      </label>

      <label className="field">
        <span>Result Limit (rows per query)</span>
        <select
          value={value.result_limit}
          disabled={running}
          onChange={(e) => set("result_limit", e.target.value)}
        >
          {config.result_limits.map((o) => (
            <option key={o.id} value={o.id}>
              {o.label}
            </option>
          ))}
        </select>
      </label>

      <div className="button-row">
        <button className="btn btn-primary" onClick={onStart} disabled={running}>
          Start Test
        </button>
        <button className="btn" onClick={onStop} disabled={!running}>
          Stop Test
        </button>
      </div>
    </div>
  );
}
