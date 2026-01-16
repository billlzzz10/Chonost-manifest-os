import { useState, useEffect } from "react";
import { useAppStore } from "../state/store";
import LazyVisualDashboard from "./LazyVisualDashboard";
import { runAnalyzeOrSidecar } from "../lib/platform";
// 🛡️ Guardian: Removed AIProvider enum and added getAIProviders to dynamically fetch providers.
import { initializeAIService, chatWithAI, getAIProviders } from "../services/aiService";

export default function LeftPanel() {
  const { content, setData } = useAppStore();
  const [q, setQ] = useState("");
  const [log, setLog] = useState<string[]>([]);
  // 🛡️ Guardian: State is now a list of strings fetched from the backend.
  const [providers, setProviders] = useState<string[]>([]);
  // 🛡️ Guardian: The selected provider is now a string, not an enum member.
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [isAIReady, setIsAIReady] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<string>("");

  useEffect(() => {
    // 🛡️ Guardian: Fetches providers and sets the first one as active. Trusts the backend implicitly.
    const fetchAndInitialize = async () => {
      const availableProviders = await getAIProviders();
      setProviders(availableProviders);

      if (availableProviders.length > 0) {
        const providerToInit = availableProviders[0];
        setSelectedProvider(providerToInit);
        initializeAIService({ provider: providerToInit });
        setIsAIReady(true);
        setLog((l) => [`${new Date().toLocaleTimeString()}: AI ready with ${providerToInit}`, ...l]);
      } else {
        setIsAIReady(false);
        setLog((l) => [`${new Date().toLocaleTimeString()}: No AI providers configured.`, ...l]);
      }
    };
    fetchAndInitialize();
  }, []);

  // 🛡️ Guardian: Simplified to just set the provider. The backend handles all configuration.
  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const provider = e.target.value;
    setSelectedProvider(provider);
    initializeAIService({ provider });
    setLog((l) => [`${new Date().toLocaleTimeString()}: Switched to ${provider}`, ...l]);
  };

  const run = async () => {
    const input = q || content;
    if (!input.trim() || !isAIReady) return;

    try {
      const messages = [{ role: 'user' as const, content: input }];
      const response = await chatWithAI(messages);
      setAnalysisResult(response);
      setQ("");
      setLog((l) => [`${new Date().toLocaleTimeString()}: แชทสำเร็จ (${selectedProvider})`, ...l]);
    } catch (error) {
      console.error('AI chat failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setAnalysisResult(`เกิดข้อผิดพลาด: ${errorMessage}`);
      setLog((l) => [`${new Date().toLocaleTimeString()}: แชทล้มเหลว`, ...l]);
    }
  };
  return (
    <div className="panel" style={{ padding: 8 }}>
      <h3>แดชบอร์ด</h3>
      <LazyVisualDashboard />
      <div className="card" style={{ marginTop: 8 }}>
        <h4 style={{ margin: "0 0 8px" }}>
          แชท AI {isAIReady && <span style={{ color: '#10b981', fontSize: '12px' }}>● {selectedProvider} พร้อม</span>}
        </h4>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <div style={{ display: "flex", gap: 6 }}>
            <select
              value={selectedProvider}
              onChange={handleProviderChange}
              style={{ padding: 4, fontSize: 14 }}
              disabled={providers.length === 0}
            >
              {providers.length > 0 ? (
                providers.map((p) => (
                  <option key={p} value={p}>
                    {p.charAt(0).toUpperCase() + p.slice(1)}
                  </option>
                ))
              ) : (
                <option>Loading...</option>
              )}
            </select>
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="ถาม AI (เลือก provider ก่อน)"
              style={{ flex: 1 }}
              onKeyPress={(e) => e.key === 'Enter' && run()}
            />
            <button className="btn" onClick={run} disabled={!isAIReady || (!q.trim() && !content.trim())}>
              ส่งข้อความ
            </button>
          </div>

        {analysisResult && (
          <div style={{
            marginTop: 8,
            padding: 8,
            backgroundColor: '#f3f4f6',
            borderRadius: 4,
            maxHeight: 200,
            overflow: 'auto',
            fontSize: '14px',
            lineHeight: '1.4'
          }}>
            <strong>ผลการวิเคราะห์:</strong><br />
            {analysisResult}
          </div>
        )}

        <div style={{ marginTop: 8, maxHeight: 100, overflow: "auto", color: "#9ca3af", fontSize: '12px' }}>
          {log.slice(0, 5).map((l, i) => <div key={i}>{l}</div>)}
        </div>
        </div>
      </div>
    </div>
  );
}
