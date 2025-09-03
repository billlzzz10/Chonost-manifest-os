import TopBar from "./components/TopBar";
import LeftPanel from "./components/LeftPanel";
import RightPanel from "./components/RightPanel";
import EditorWhiteboard from "./components/EditorWhiteboard";
import RotaryPalette from "./components/RotaryPalette";

export default function App() {
  return (
    <div className="app">
      <TopBar />
      <div className="layout">
        <LeftPanel />
        <EditorWhiteboard />
        <RightPanel />
      </div>
      <RotaryPalette />
    </div>
  );
}
