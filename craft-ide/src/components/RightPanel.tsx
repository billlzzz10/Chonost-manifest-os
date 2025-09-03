import { useMemo, useState, useEffect, useRef } from "react";
import { useStore } from "../state/store";
import mermaid from "mermaid";
import { toMindmap } from "../lib/platform";

mermaid.initialize({
  startOnLoad: false,
  securityLevel: "loose",
  theme: "dark",
});

export default function RightPanel() {
  const [tab, setTab] = useState<"tree" | "graph" | "files" | "settings">(
    "tree"
  );
  const { content } = useStore();

  const mm = useMemo(() => {
    const lines = content.split("\n").map((s) => s.trim());
    const title = lines.find((l) => l.startsWith("# "))?.slice(2) || "Mindmap";
    const bullets = lines
      .filter((l) => l.startsWith("- "))
      .map((l) => l.slice(2));
    return toMindmap(
      title,
      bullets.length ? bullets : ["Add - bullets in markdown"]
    );
  }, [content]);

  const containerRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (tab !== "graph" || !containerRef.current) return;
    let cancelled = false;
    (async () => {
      try {
        const { svg } = await mermaid.render(
          "mm-" + Math.random().toString(36).slice(2),
          mm
        );
        if (!cancelled && containerRef.current)
          containerRef.current.innerHTML = svg;
      } catch (e) {
        if (containerRef.current)
          containerRef.current.innerHTML = `<pre style="color:#f87171">Mermaid error</pre>`;
      }
    })();
    return () => {
      cancelled = true;
      if (containerRef.current) containerRef.current.innerHTML = "";
    };
  }, [tab, mm]);

  return (
    <div className="panel">
      <div className="tabs">
        <button className="btn" onClick={() => setTab("tree")}>
          Tree
        </button>
        <button className="btn" onClick={() => setTab("graph")}>
          Graph
        </button>
        <button className="btn" onClick={() => setTab("files")}>
          Files
        </button>
        <button className="btn" onClick={() => setTab("settings")}>
          Settings
        </button>
      </div>
      <div
        className="card"
        style={{ height: "calc(100% - 44px)", overflow: "auto" }}
      >
        {tab === "tree" && (
          <pre>
            • root{"\n"} ├─ docs{"\n"} └─ assets
          </pre>
        )}
        {tab === "graph" && <div ref={containerRef} />}
        {tab === "files" && <div>File explorer stub</div>}
        {tab === "settings" && <div>Plugin settings stub</div>}
      </div>
    </div>
  );
}
