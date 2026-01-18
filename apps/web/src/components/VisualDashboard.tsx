import { Bar, PolarArea } from "react-chartjs-2";
import {
  Chart as C,
  BarElement,
  CategoryScale,
  LinearScale,
  RadialLinearScale,
  Tooltip,
  Legend,
} from "chart.js";
import { useAppStore } from "../state/store";
import React from "react";

C.register(
  BarElement,
  CategoryScale,
  LinearScale,
  RadialLinearScale,
  Tooltip,
  Legend
);

// This component renders the charts and is memoized to prevent unnecessary re-renders.
// It will only re-render if the `topKeywords` prop changes, which is a performance
// optimization that avoids expensive chart re-draws when other data updates.
const MemoizedCharts = React.memo(function MemoizedCharts({
  topKeywords,
}: {
  topKeywords: { keyword: string; weight: number }[];
}) {
  const labels = topKeywords.map((k) => k.keyword);
  const values = topKeywords.map((k) => k.weight);
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
      <div>
        <Bar
          data={{ labels, datasets: [{ label: "keywords", data: values }] }}
        />
      </div>
      <div>
        <PolarArea
          data={{ labels, datasets: [{ label: "keywords", data: values }] }}
        />
      </div>
    </div>
  );
});

export default function VisualDashboard() {
  const { data } = useAppStore();
  return (
    <div className="card">
      <h4 style={{ margin: "0 0 8px" }}>Metrics</h4>
      {/* The MemoizedCharts component is used here to ensure the charts do not re-render
      unless the keyword data has changed. This is a key performance optimization. */}
      <MemoizedCharts topKeywords={data.topKeywords} />
      <div style={{ marginTop: 8, display: "flex", gap: 8, flexWrap: "wrap" }}>
        <span className="badge">sentiment {data.sentiment.toFixed(2)}</span>
        <span className="badge">words {data.wordCount}</span>
      </div>
    </div>
  );
}
