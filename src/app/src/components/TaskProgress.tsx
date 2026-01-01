import { useAppStore } from "../state/store";

export default function TaskProgress() {
  const task = useAppStore((state) =>
    state.tasks.length > 0 ? state.tasks[state.tasks.length - 1] : null
  );

  if (!task) {
    return null;
  }

  return (
    <span className="badge" style={{ marginLeft: 8 }}>
      {task.title}: {task.progress}%
    </span>
  );
}
