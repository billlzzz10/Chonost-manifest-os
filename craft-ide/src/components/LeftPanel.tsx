import { useState } from "react";
import { useStore } from "../state/store";
import VisualDashboard from "./VisualDashboard";
import { runAnalyzeOrSidecar } from "../lib/platform";

export default function LeftPanel() {
  const { content, setData } = useStore();
  const [q, setQ] = useState(""); const [log, setLog] = useState<string[]>([]);
  const run = async () => {
    const res = await runAnalyzeOrSidecar(q || content);
    setData(res); setQ(""); setLog((l) => [`${new Date().toLocaleTimeString()}: analyzed`, ...l]);
  };
  return (
    <div className="panel" style={{ padding: 8 }}>
      <h3>Dashboard</h3>
      <VisualDashboard />
      <div className="card" style={{ marginTop: 8 }}>
        <h4 style={{ margin: "0 0 8px" }}>Chat</h4>
        <div style={{ display: "flex", gap: 6 }}>
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="ถาม หรือวิเคราะห์ข้อความ" style={{ flex: 1 }} />
          <button className="btn" onClick={run}>Run</button>
        </div>
        <div style={{ marginTop: 8, maxHeight: 140, overflow: "auto", color: "#9ca3af" }}>
          {log.map((l, i) => <div key={i}>{l}</div>)}
        </div>
      </div>
    </div>
  );
}
