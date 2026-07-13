import type { ReactNode } from "react";

export function Section({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="section">
      <h3 className="section-title">{title}</h3>
      {children}
    </section>
  );
}

export function MetricGrid({
  columns = 3,
  children,
}: {
  columns?: number;
  children: ReactNode;
}) {
  return (
    <div
      className="metric-grid"
      style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}
    >
      {children}
    </div>
  );
}

export function Metric({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div className="metric" title={hint}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
    </div>
  );
}

export function Banner({
  kind,
  children,
}: {
  kind: "success" | "info" | "warning" | "error";
  children: ReactNode;
}) {
  return <div className={`banner banner-${kind}`}>{children}</div>;
}
