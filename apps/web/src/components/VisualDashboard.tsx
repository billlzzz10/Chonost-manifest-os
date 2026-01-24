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
import { shallow } from "zustand/shallow";
C.register(
  BarElement,
  CategoryScale,
  LinearScale,
  RadialLinearScale,
  Tooltip,
  Legend
);

export default function VisualDashboard() {
  const { topKeywords, sentiment, wordCount } = useAppStore(
    (state) => ({
      // By selecting only the specific properties needed, this component
      // will only re-render when these values change, not on any
      // other state update. This is a significant performance optimization.
      topKeywords: state.data.topKeywords,
      sentiment: state.data.sentiment,
      wordCount: state.data.wordCount,
    }),
    shallow
  );
  const labels = topKeywords.map((k) => k.keyword);
  const values = topKeywords.map((k) => k.weight);
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
        <span className="badge">sentiment {sentiment.toFixed(2)}</span>
        <span className="badge">words {wordCount}</span>
      </div>
    </div>
  );
}
