import { useAppStore } from "../state/store";
import React from "react";

// ⚡ Bolt: Memoize TopBar and use a specific selector for the last task
// to prevent re-renders when other tasks in the list change.
export default React.memo(function TopBar() {
  const setMode = useAppStore((s) => s.setMode);
  const enqueue = useAppStore((s) => s.enqueue);
  const updateTask = useAppStore((s) => s.updateTask);
  const lastTask = useAppStore((s) => s.tasks.at(-1));

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
        แก้ไข
      </button>
      <button className="btn" onClick={() => setMode("whiteboard")}>
        ไวท์บอร์ด
      </button>
      <button className="btn" onClick={() => setMode("reading")}>
        อ่าน
      </button>
      <div style={{ marginLeft: "auto" }} />
      <button className="btn primary" onClick={startIngest}>
        สร้างดัชนี RAG
      </button>
      {lastTask && (
        <span key={lastTask.id} className="badge" style={{ marginLeft: 8 }}>
          {lastTask.title}: {lastTask.progress}%
        </span>
      )}
    </div>
  );
});
