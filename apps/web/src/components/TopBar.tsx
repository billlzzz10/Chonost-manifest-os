import { useAppStore } from "../state/store";

export default function TopBar() {
  const { setMode, tasks, enqueue, updateTask } = useAppStore();
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
  const isIngesting = tasks.some((t) => t.status === "running");
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
      <button className="btn primary" onClick={startIngest} disabled={isIngesting}>
        {isIngesting ? "กำลังสร้าง..." : "สร้างดัชนี RAG"}
      </button>
      {tasks.slice(-1).map((t) => (
        <span key={t.id} className="badge" style={{ marginLeft: 8 }}>
          {t.title}: {t.progress}%
        </span>
      ))}
    </div>
  );
}
