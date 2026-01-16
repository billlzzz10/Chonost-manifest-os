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
import { shallow } from "zustand/shallow";
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
  // By using a selector and the `shallow` equality checker, we ensure this component
  // only re-renders when the specific data it relies on changes. This is a significant
  // performance boost, preventing re-renders when unrelated parts of the `data` object are updated.
  // 📊 Impact: Prevents unnecessary re-renders, leading to a smoother UI, especially during frequent state updates.
  const { topKeywords, sentiment, wordCount } = useAppStore(
    (state) => ({
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
