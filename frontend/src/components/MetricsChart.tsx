import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { EvalMetrics } from "../types";

const STRATEGY_COLORS: Record<string, string> = {
  bm25: "#fbbf24",
  dense: "#818cf8",
  hybrid: "#34d399",
};

const STRATEGY_LABELS: Record<string, string> = {
  bm25: "BM25",
  dense: "Dense",
  hybrid: "Hybrid + Rerank",
};

export default function MetricsChart({ results }: { results: Record<string, EvalMetrics> }) {
  const strategies = Object.keys(results);
  if (strategies.length === 0) return null;

  const metricNames = Object.keys(results[strategies[0]]);
  const data = metricNames.map((metric) => {
    const row: Record<string, string | number> = { metric };
    for (const s of strategies) row[s] = results[s][metric];
    return row;
  });

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} barGap={3}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
        <XAxis
          dataKey="metric"
          stroke="rgba(255,255,255,0.3)"
          tick={{ fill: "#71717a", fontSize: 11.5 }}
          axisLine={{ stroke: "rgba(255,255,255,0.08)" }}
          tickLine={false}
        />
        <YAxis
          stroke="rgba(255,255,255,0.3)"
          tick={{ fill: "#71717a", fontSize: 11.5 }}
          domain={[0, 1]}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          cursor={{ fill: "rgba(255,255,255,0.03)" }}
          contentStyle={{
            background: "#14161d",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 10,
            fontSize: 12.5,
          }}
          labelStyle={{ color: "#e4e4e7", fontWeight: 600, marginBottom: 4 }}
          itemStyle={{ padding: "1px 0" }}
        />
        <Legend
          wrapperStyle={{ fontSize: 12.5, paddingTop: 12 }}
          formatter={(value) => <span style={{ color: "#a1a1aa" }}>{STRATEGY_LABELS[value] ?? value}</span>}
        />
        {strategies.map((s) => (
          <Bar key={s} dataKey={s} fill={STRATEGY_COLORS[s] ?? "#888"} name={s} radius={[4, 4, 0, 0]} maxBarSize={28} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
