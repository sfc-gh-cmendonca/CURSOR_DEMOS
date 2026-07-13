import type { TestStatusResponse } from "../api/types";
import { Banner, Metric, MetricGrid, Section } from "./ui";
import { BarChartCard, LineChartCard } from "./charts";
import { histogram, mean, percentile, toNumber } from "../lib/stats";
import { kb, mb, msFromMs, num, pct } from "../lib/format";

export function ResultsDashboard({ test }: { test: TestStatusResponse | null }) {
  if (!test) {
    return (
      <Banner kind="info">
        Configure and start a test run to see performance results here.
      </Banner>
    );
  }

  if (test.status === "error") {
    return <Banner kind="error">Test failed: {test.error}</Banner>;
  }

  if (test.status === "queued" || test.status === "running") {
    return (
      <Banner kind="info">
        Running JDBC load test on <code>{test.warehouse}</code>:{" "}
        {test.config.num_connections} connections &times;{" "}
        {test.config.duration_seconds}s. Polling for results...
      </Banner>
    );
  }

  const results = test.results;
  if (!results || results.latencies.length === 0) {
    return (
      <Banner kind="warning">
        No queries completed during the test run.
        {results?.error_messages?.length ? (
          <ul>
            {results.error_messages.map((m, i) => (
              <li key={i}>{m}</li>
            ))}
          </ul>
        ) : null}
      </Banner>
    );
  }

  const latencies = results.latencies;
  const avg = mean(latencies);
  const p50 = percentile(latencies, 0.5);
  const p95 = percentile(latencies, 0.95);
  const p99 = percentile(latencies, 0.99);
  const min = Math.min(...latencies);
  const max = Math.max(...latencies);
  const qps = results.elapsed_total > 0 ? results.query_count / results.elapsed_total : 0;

  const clientLatencyData = latencies.map((l, i) => ({
    query: i + 1,
    latency: Number((l * 1000).toFixed(2)),
  }));
  const clientHist = histogram(latencies.map((l) => l * 1000)).map((b) => ({
    label: b.label,
    count: b.count,
  }));

  const connTimeline = (results.conn_timeline ?? []).map(([t, c]) => ({
    time: Number(t.toFixed(1)),
    active: c,
  }));

  const stats = test.server_stats;
  const hasServer = !!stats && toNumber(stats["TOTAL_QUERIES"]) > 0;
  const details = test.server_details ?? [];

  const apiLabel =
    results.session_v1_query_api === "true" || results.session_v1_query_api === "True"
      ? "V1"
      : results.session_v1_query_api === "false" ||
          results.session_v1_query_api === "False"
        ? "V2"
        : results.session_v1_query_api ?? "unknown";

  return (
    <div className="results">
      <Banner kind="success">
        Test completed: <strong>{num(results.query_count)}</strong> queries across{" "}
        <strong>{results.num_connections}</strong> JDBC connections in{" "}
        <strong>{results.elapsed_total.toFixed(1)}s</strong>
      </Banner>

      <Section title="Overview">
        <MetricGrid columns={6}>
          <Metric label="Queries/sec (QPS)" value={qps.toFixed(2)} />
          <Metric label="Total Queries" value={num(results.query_count)} />
          <Metric label="Errors" value={num(results.errors)} />
          <Metric label="JDBC Connections" value={num(results.num_connections)} />
          <Metric label="Unique Tickers" value={num(results.unique_tickers)} />
          <Metric
            label="Avg Rows/Query"
            value={num(toNumber(results.avg_rows_per_query))}
          />
        </MetricGrid>
      </Section>

      <Section title="Result Transfer Details">
        <MetricGrid columns={3}>
          <Metric label="Avg Rows / Query" value={num(toNumber(results.avg_rows_per_query))} />
          <Metric label="Max Rows / Query" value={num(toNumber(results.max_rows_per_query))} />
          <Metric label="CLIENT_RESULT_CHUNK_SIZE" value="16 MB" />
        </MetricGrid>
        <MetricGrid columns={3}>
          <Metric label="1 Chunk" value={num(toNumber(results.chunks_1))} />
          <Metric label="2 Chunks" value={num(toNumber(results.chunks_2))} />
          <Metric label="3+ Chunks" value={num(toNumber(results.chunks_3plus))} />
        </MetricGrid>
      </Section>

      <Section title="JDBC Session Parameters (from server)">
        <MetricGrid columns={2}>
          <Metric label="Query API Version" value={apiLabel} />
          <Metric
            label="Prefetch Threads"
            value={results.session_prefetch_threads ?? "unknown"}
          />
        </MetricGrid>
      </Section>

      <Section title="Client-Side Latency (end-to-end incl. network)">
        <MetricGrid columns={3}>
          <Metric label="Avg Latency" value={msFromMs(avg * 1000)} />
          <Metric label="P50 (Median)" value={msFromMs(p50 * 1000)} />
          <Metric label="P95" value={msFromMs(p95 * 1000)} />
        </MetricGrid>
        <MetricGrid columns={3}>
          <Metric label="P99" value={msFromMs(p99 * 1000)} />
          <Metric label="Min" value={msFromMs(min * 1000)} />
          <Metric label="Max" value={msFromMs(max * 1000)} />
        </MetricGrid>
      </Section>

      {hasServer && stats && (
        <>
          <Section title="Server-Side Metrics (from INFORMATION_SCHEMA)">
            <MetricGrid columns={3}>
              <Metric label="Queries Served" value={num(results.query_count)} />
              <Metric label="Successful" value={num(toNumber(stats["SUCCESSFUL_QUERIES"]))} />
              <Metric label="Failed" value={num(toNumber(stats["FAILED_QUERIES"]))} />
            </MetricGrid>
            <MetricGrid columns={3}>
              <Metric
                label="Avg Compilation"
                value={msFromMs(toNumber(stats["AVG_COMPILATION_TIME_MS"]))}
              />
              <Metric
                label="Avg Execution"
                value={msFromMs(toNumber(stats["AVG_EXECUTION_TIME_MS"]))}
              />
              <Metric
                label="Median (P50)"
                value={msFromMs(toNumber(stats["MEDIAN_DURATION_MS"]))}
              />
            </MetricGrid>
            <MetricGrid columns={3}>
              <Metric label="Min Duration" value={msFromMs(toNumber(stats["MIN_DURATION_MS"]))} />
              <Metric label="Avg Duration" value={msFromMs(toNumber(stats["AVG_DURATION_MS"]))} />
              <Metric label="Max Duration" value={msFromMs(toNumber(stats["MAX_DURATION_MS"]))} />
            </MetricGrid>
            <MetricGrid columns={3}>
              <Metric label="P95 Duration" value={msFromMs(toNumber(stats["P95_DURATION_MS"]))} />
              <Metric label="P99 Duration" value={msFromMs(toNumber(stats["P99_DURATION_MS"]))} />
              <Metric
                label="Total Bytes Scanned"
                value={mb(toNumber(stats["TOTAL_BYTES_SCANNED"]))}
              />
            </MetricGrid>
            <MetricGrid columns={3}>
              <Metric
                label="Total Rows Produced"
                value={num(toNumber(stats["TOTAL_ROWS_PRODUCED"]))}
              />
              <Metric label="Avg Bytes / Row" value={toNumber(stats["AVG_BYTES_PER_ROW"]).toFixed(1)} />
              <Metric label="Avg Result Size" value={kb(toNumber(stats["AVG_RESULT_BYTES"]))} />
            </MetricGrid>
          </Section>

          {details.length > 0 && (
            <>
              <Section title="Server-Side Latency Over Time">
                <LineChartCard
                  data={details.map((d, i) => ({
                    query: i + 1,
                    duration: toNumber(d.TOTAL_ELAPSED_TIME),
                  }))}
                  xKey="query"
                  series={[{ key: "duration", color: "#38bdf8", name: "Duration (ms)" }]}
                />
              </Section>

              <Section title="Server-Side Latency Histogram">
                <BarChartCard
                  data={histogram(details.map((d) => toNumber(d.TOTAL_ELAPSED_TIME))).map((b) => ({
                    label: b.label,
                    count: b.count,
                  }))}
                  xKey="label"
                  barKey="count"
                  color="#818cf8"
                />
              </Section>

              <Section title="Compilation vs Execution Time">
                <LineChartCard
                  data={details.map((d, i) => ({
                    query: i + 1,
                    compilation: toNumber(d.COMPILATION_TIME),
                    execution: toNumber(d.EXECUTION_TIME),
                  }))}
                  xKey="query"
                  series={[
                    { key: "compilation", color: "#f59e0b", name: "Compilation" },
                    { key: "execution", color: "#10b981", name: "Execution" },
                  ]}
                />
              </Section>

              <Section title="Queue Time (Overload)">
                <LineChartCard
                  data={details.map((d, i) => ({
                    query: i + 1,
                    queue: toNumber(d.QUEUED_OVERLOAD_TIME),
                  }))}
                  xKey="query"
                  series={[{ key: "queue", color: "#ef4444", name: "Queue Time (ms)" }]}
                />
                <MetricGrid columns={3}>
                  <Metric
                    label="Queries Queued"
                    value={num(details.filter((d) => toNumber(d.QUEUED_OVERLOAD_TIME) > 0).length)}
                  />
                  <Metric
                    label="Avg Queue Time"
                    value={msFromMs(mean(details.map((d) => toNumber(d.QUEUED_OVERLOAD_TIME))))}
                  />
                  <Metric
                    label="Max Queue Time"
                    value={msFromMs(Math.max(...details.map((d) => toNumber(d.QUEUED_OVERLOAD_TIME)), 0))}
                  />
                </MetricGrid>
              </Section>
            </>
          )}

          {test.cluster_stats && test.cluster_stats.length > 0 && (
            <Section title="Queries Served per Cluster">
              <BarChartCard
                data={test.cluster_stats.map((c) => ({
                  cluster: `Cluster ${c.CLUSTER_NUMBER}`,
                  queries: toNumber(c.QUERIES_SERVED),
                }))}
                xKey="cluster"
                barKey="queries"
                color="#34d399"
              />
            </Section>
          )}
        </>
      )}

      {test.cache_stats && toNumber(test.cache_stats["TOTAL_QUERIES"]) > 0 && (
        <Section title="Cache Performance (from ACCOUNT_USAGE)">
          <MetricGrid columns={4}>
            <Metric
              label="Result Cache"
              value={pct(
                (toNumber(test.cache_stats["RESULT_CACHE_HITS"]) /
                  toNumber(test.cache_stats["TOTAL_QUERIES"])) *
                  100,
              )}
            />
            <Metric
              label="Warehouse Cache"
              value={pct(
                (toNumber(test.cache_stats["WAREHOUSE_CACHE_HITS"]) /
                  toNumber(test.cache_stats["TOTAL_QUERIES"])) *
                  100,
              )}
            />
            <Metric
              label="Partial Cache"
              value={pct(
                (toNumber(test.cache_stats["PARTIAL_CACHE_HITS"]) /
                  toNumber(test.cache_stats["TOTAL_QUERIES"])) *
                  100,
              )}
            />
            <Metric
              label="Remote Storage"
              value={pct(
                (toNumber(test.cache_stats["STORAGE_READS"]) /
                  toNumber(test.cache_stats["TOTAL_QUERIES"])) *
                  100,
              )}
            />
          </MetricGrid>
          <BarChartCard
            data={[
              {
                label: "Warehouse Cache",
                bytes: Number(mb(toNumber(test.cache_stats["BYTES_FROM_CACHE"])).replace(" MB", "")),
              },
              {
                label: "Remote Storage",
                bytes: Number(mb(toNumber(test.cache_stats["BYTES_FROM_STORAGE"])).replace(" MB", "")),
              },
            ]}
            xKey="label"
            barKey="bytes"
            color="#38bdf8"
          />
        </Section>
      )}

      <Section title="Active JDBC Connections Over Time">
        {connTimeline.length > 0 ? (
          <LineChartCard
            data={connTimeline}
            xKey="time"
            series={[{ key: "active", color: "#a78bfa", name: "Active Connections" }]}
          />
        ) : (
          <Banner kind="info">No connection timeline captured.</Banner>
        )}
      </Section>

      <Section title="Client-Side Latency Over Time">
        <LineChartCard
          data={clientLatencyData}
          xKey="query"
          series={[{ key: "latency", color: "#38bdf8", name: "Latency (ms)" }]}
        />
      </Section>

      <Section title="Client-Side Latency Histogram">
        <BarChartCard data={clientHist} xKey="label" barKey="count" color="#818cf8" />
      </Section>

      {results.errors > 0 && results.error_messages.length > 0 && (
        <Section title="Errors">
          {results.error_messages.map((m, i) => (
            <Banner kind="error" key={i}>
              {m}
            </Banner>
          ))}
        </Section>
      )}
    </div>
  );
}
