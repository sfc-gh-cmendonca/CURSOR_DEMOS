import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const AXIS_COLOR = "#64748b";
const GRID_COLOR = "#1e293b";

interface SeriesDef {
  key: string;
  color: string;
  name?: string;
}

export function LineChartCard({
  data,
  xKey,
  series,
  height = 240,
}: {
  data: Record<string, number | string>[];
  xKey: string;
  series: SeriesDef[];
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} />
        <XAxis dataKey={xKey} stroke={AXIS_COLOR} tick={{ fontSize: 11 }} />
        <YAxis stroke={AXIS_COLOR} tick={{ fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            background: "#0f172a",
            border: "1px solid #1e293b",
            borderRadius: 8,
          }}
        />
        {series.map((s) => (
          <Line
            key={s.key}
            type="monotone"
            dataKey={s.key}
            name={s.name ?? s.key}
            stroke={s.color}
            dot={false}
            strokeWidth={2}
            isAnimationActive={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

export function BarChartCard({
  data,
  xKey,
  barKey,
  color = "#38bdf8",
  height = 240,
}: {
  data: Record<string, number | string>[];
  xKey: string;
  barKey: string;
  color?: string;
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID_COLOR} />
        <XAxis dataKey={xKey} stroke={AXIS_COLOR} tick={{ fontSize: 11 }} />
        <YAxis stroke={AXIS_COLOR} tick={{ fontSize: 11 }} />
        <Tooltip
          cursor={{ fill: "rgba(148,163,184,0.1)" }}
          contentStyle={{
            background: "#0f172a",
            border: "1px solid #1e293b",
            borderRadius: 8,
          }}
        />
        <Bar dataKey={barKey} fill={color} isAnimationActive={false} />
      </BarChart>
    </ResponsiveContainer>
  );
}
