import { useState } from "react";
import { useAppStore } from "../state/store";

export default function StickyNotes() {
  const { notes, updateNote, removeNote, addNote } = useAppStore();
  return (
    <>
      {notes.map((n) => (
        <Note
          key={n.id}
          {...n}
          onMove={(p) => updateNote(n.id, p)}
          onRemove={() => removeNote(n.id)}
        />
      ))}
      <button
        type="button"
        className="btn"
        style={{ position: "absolute", right: 12, top: 8, zIndex: 10 }}
        onClick={() =>
          addNote({ id: "note-" + Date.now(), x: 24, y: 24, text: "note" })
        }
      >
        + Note
      </button>
    </>
  );
}

function Note(props: {
  id: string;
  x: number;
  y: number;
  text: string;
  onMove: (p: Partial<{ x: number; y: number; text: string }>) => void;
  onRemove: () => void;
}) {
  const [drag, setDrag] = useState<{ dx: number; dy: number } | null>(null);
  return (
    <div
      className="sticky"
      style={{ left: props.x, top: props.y }}
      onMouseDown={(e) =>
        setDrag({ dx: e.clientX - props.x, dy: e.clientY - props.y })
      }
      onMouseMove={(e) =>
        drag && props.onMove({ x: e.clientX - drag.dx, y: e.clientY - drag.dy })
      }
      onMouseUp={() => setDrag(null)}
      onMouseLeave={() => setDrag(null)}
    >
      <button className="x" onClick={props.onRemove}>
        ×
      </button>
      <textarea
        value={props.text}
        onChange={(e) => props.onMove({ text: e.target.value })}
        title="Note content"
      />
    </div>
  );
}
