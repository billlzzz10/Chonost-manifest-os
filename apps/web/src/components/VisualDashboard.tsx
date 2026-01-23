import { useMemo } from "react";
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
C.register(
  BarElement,
  CategoryScale,
  LinearScale,
  RadialLinearScale,
  Tooltip,
  Legend
);

export default function VisualDashboard() {
  const { data } = useAppStore();
  // Bolt ⚡: Memoize chart data to prevent re-calculation on every render.
  // This avoids unnecessary processing when other state in the app updates.
  const labels = useMemo(
    () => data.topKeywords.map((k) => k.keyword),
    [data.topKeywords]
  );
  const values = useMemo(
    () => data.topKeywords.map((k) => k.weight),
    [data.topKeywords]
  );
  return (
    <div className="card">
      <h4 style={{ margin: "0 0 8px" }}>Metrics</h4>
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
      <div style={{ marginTop: 8, display: "flex", gap: 8, flexWrap: "wrap" }}>
        <span className="badge">sentiment {data.sentiment.toFixed(2)}</span>
        <span className="badge">words {data.wordCount}</span>
      </div>
    </div>
  );
}
