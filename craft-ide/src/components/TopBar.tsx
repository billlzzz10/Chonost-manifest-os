import { useStore } from "../state/store";

export default function TopBar() {
  const { setMode, tasks, enqueue, updateTask } = useStore();
  const startIngest = () => {
    const id = "ing-" + Date.now();
    enqueue({ id, title: "Index RAG", progress: 0, status: "running" });
    let p = 0;
    const t = setInterval(() => {
      p += 12;
      if (p >= 100) {
        updateTask(id, { progress: 100, status: "done" });
        clearInterval(t);
      } else updateTask(id, { progress: p });
    }, 250);
  };
  return (
    <div className="topbar">
      <div className="title">Craft IDE</div>
      <button className="btn" onClick={() => setMode("editor")}>
        Editor
      </button>
      <button className="btn" onClick={() => setMode("whiteboard")}>
        Whiteboard
      </button>
      <button className="btn" onClick={() => setMode("reading")}>
        Reading
      </button>
      <div style={{ marginLeft: "auto" }} />
      <button className="btn primary" onClick={startIngest}>
        Index RAG
      </button>
      {tasks.slice(-1).map((t) => (
        <span key={t.id} className="badge" style={{ marginLeft: 8 }}>
          {t.title}: {t.progress}%
        </span>
      ))}
    </div>
  );
}
