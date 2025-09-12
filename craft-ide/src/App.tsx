import TopBar from "./components/TopBar";
import LeftPanel from "./components/LeftPanel";
import RightPanel from "./components/RightPanel";
import EditorWhiteboard from "./components/EditorWhiteboard";
import ReadingView from "./components/ReadingView";
import StickyNotes from "./components/StickyNotes";
import RotaryPalette from "./components/RotaryPalette";
import VisualDashboard from "./components/VisualDashboard";

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
      <ReadingView content="" />
      <StickyNotes />
      <VisualDashboard />
    </div>
  );
}
