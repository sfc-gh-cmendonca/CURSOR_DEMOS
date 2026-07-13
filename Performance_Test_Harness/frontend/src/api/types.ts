export interface Option {
  id: string;
  label: string;
}

export interface TableOption extends Option {
  table: string;
  warehouse: string;
}

export interface ConfigDefaults {
  table_id: string;
  query_mix: string;
  exec_mode: string;
  ticker_bias: string;
  num_connections: number;
  duration_seconds: number;
  result_limit: string;
}

export interface ConfigResponse {
  tables: TableOption[];
  query_mixes: Option[];
  exec_modes: Option[];
  ticker_biases: Option[];
  result_limits: Option[];
  defaults: ConfigDefaults;
}

export interface TestConfigRequest {
  table_id: string;
  query_mix: string;
  exec_mode: string;
  ticker_bias: string;
  num_connections: number;
  duration_seconds: number;
  result_limit: string;
}

export interface StartTestResponse {
  test_id: string;
  status: string;
}

export interface LoadTestResults {
  latencies: number[];
  query_count: number;
  errors: number;
  elapsed_total: number;
  num_connections: number;
  unique_tickers: number;
  avg_rows_per_query?: number;
  max_rows_per_query?: number;
  chunks_1?: number;
  chunks_2?: number;
  chunks_3plus?: number;
  test_start_ts: string;
  test_end_ts: string;
  conn_timeline: [number, number][];
  error_messages: string[];
  session_v1_query_api?: string;
  session_prefetch_threads?: string;
}

export interface ServerDetailRow {
  QUERY_ID: string;
  TOTAL_ELAPSED_TIME: number;
  EXECUTION_TIME: number;
  COMPILATION_TIME: number;
  BYTES_SCANNED: number;
  ROWS_PRODUCED: number;
  EXECUTION_STATUS: string;
  START_TIME: string;
  CLUSTER_NUMBER: number | null;
  QUEUED_OVERLOAD_TIME: number;
}

export interface ClusterRow {
  CLUSTER_NUMBER: number;
  QUERIES_SERVED: number;
}

export type StatusValue =
  | "queued"
  | "running"
  | "completed"
  | "error"
  | "stopped";

export interface TestStatusResponse {
  test_id: string;
  status: StatusValue;
  config: TestConfigRequest;
  table: string | null;
  warehouse: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  error: string | null;
  results: LoadTestResults | null;
  server_stats: Record<string, number | null> | null;
  server_details: ServerDetailRow[] | null;
  cluster_stats: ClusterRow[] | null;
  cache_stats: Record<string, number | null> | null;
}
