import { useEffect, useMemo, useState } from "react";
import { useAppStore } from "../state/store";
import { runPaletteItem } from "../lib/platform";

function Wheel({ side, labels }: { side: "left" | "right"; labels: string[] }) {
  const items = useAppStore((s) => (side === "left" ? s.leftPalette : s.rightPalette));
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if (e.altKey && /q/i.test(e.key) && side === "left") setOpen((v) => !v);
      if (e.altKey && /w/i.test(e.key) && side === "right") setOpen((v) => !v);
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [side]);
  const angles = useMemo(() => [0, 60, 120, 180, 240, 300].map((d) => (d * Math.PI) / 180), []);
  return (
    <div className="p">
      <div className="wheel">
        {open &&
          items.map((it, i) => (
            <button
              key={i}
              className="slot"
              style={{
                left: `calc(50% + ${Math.cos(angles[i]) * 60}px - 42px)`,
                top: `calc(50% + ${Math.sin(angles[i]) * 60}px - 18px)`
              }}
              onClick={() => runPaletteItem(it)}
              title={`${it.kind}: ${"label" in it ? it.label : ""}`}
            >
              {labels[i] || ("label" in it ? it.label : String(i))}
            </button>
          ))}
        <div
          style={{
            opacity: 0.9,
            fontSize: 14,
            backgroundColor: "rgba(255, 255, 255, 0.1)",
            padding: "2px 6px",
            borderRadius: "4px",
            border: "1px solid rgba(255, 255, 255, 0.2)"
          }}
        >
          Alt+{side === "left" ? "Q" : "W"}
        </div>
      </div>
    </div>
  );
}

export default function RotaryPalette() {
  return (
    <div className="rotary">
      <Wheel side="left" labels={["G", "C", "Y", "Pen", "Erase", "Analyze"]} />
      <Wheel side="right" labels={["Ruler", "Script", "Clear", "Pink", "Orange", "White"]} />
    </div>
  );
}
