import { useAppStore } from "../state/store";
import { shallow } from "zustand/shallow";
import TaskProgress from "./TaskProgress";

export default function TopBar() {
  // ⚡ Bolt: Optimized `useAppStore` selector.
  // By selecting only the functions (`setMode`, `enqueue`, `updateTask`),
  // this component will not re-render when the `tasks` array changes.
  // The `shallow` comparison function prevents re-renders if the selected
  // object is shallowly equal.
  const { setMode, enqueue, updateTask } = useAppStore(
    (state) => ({
      setMode: state.setMode,
      enqueue: state.enqueue,
      updateTask: state.updateTask,
    }),
    shallow
  );

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
      {/* ⚡ Bolt: Re-rendering is now isolated to the TaskProgress component. */}
      <TaskProgress />
    </div>
  );
}
