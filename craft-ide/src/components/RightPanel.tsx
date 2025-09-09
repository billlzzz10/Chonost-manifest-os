import { useMemo, useState, useEffect, useRef } from "react";
import { useAppStore } from "../state/store";
import { invoke } from "@tauri-apps/api/tauri";
import mermaid from "mermaid";
import { toMindmap } from "../lib/platform";

mermaid.initialize({
  startOnLoad: false,
  securityLevel: "loose",
  theme: "dark",
});

export default function RightPanel() {
  const [tab, setTab] = useState<"tree" | "graph" | "files" | "settings">(
    "tree",
  );
  const { content, setContent, setCurrentFile } = useAppStore();

  // File explorer state
  const [currentDir, setCurrentDir] = useState<string>(".");
  const [fileTree, setFileTree] = useState<any[]>([]);
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);

  // Context menu state
  const [contextMenu, setContextMenu] = useState<{
    visible: boolean;
    x: number;
    y: number;
    file?: any;
  }>({ visible: false, x: 0, y: 0 });

  // Modal state for file/folder naming
  const [modal, setModal] = useState<{
    visible: boolean;
    type: "file" | "folder" | null;
    value: string;
    error: string;
  }>({ visible: false, type: null, value: "", error: "" });

  // Load directory contents
  const loadDirectory = async (dirPath: string) => {
    setLoading(true);
    try {
      const result = await invoke("list_dir", { path: dirPath });
      setFileTree(result as any[]);
    } catch (error) {
      console.error("Failed to load directory:", error);
      setFileTree([]);
    }
    setLoading(false);
  };

  // Handle file double-click
  const handleFileDoubleClick = async (file: any) => {
    if (file.is_dir) {
      // Toggle directory expansion
      const newExpanded = new Set(expandedDirs);
      if (newExpanded.has(file.path)) {
        newExpanded.delete(file.path);
      } else {
        newExpanded.add(file.path);
      }
      setExpandedDirs(newExpanded);
    } else {
      // Load file content
      try {
        const content = await invoke("read_file", { path: file.path });
        setContent(content as string);
        setCurrentFile(file.path);
      } catch (error) {
        console.error("Failed to read file:", error);
      }
    }
  };

  // Handle right-click context menu
  const handleContextMenu = (e: React.MouseEvent, file: any) => {
    e.preventDefault();
    setContextMenu({
      visible: true,
      x: e.clientX,
      y: e.clientY,
      file,
    });
  };

  // Hide context menu
  const hideContextMenu = () => {
    setContextMenu({ visible: false, x: 0, y: 0 });
  };

  // Context menu actions
  const handleDelete = async () => {
    if (!contextMenu.file) return;
    try {
      await invoke("delete_file", { path: contextMenu.file.path });
      loadDirectory(currentDir); // Refresh
    } catch (error) {
      console.error("Failed to delete:", error);
    }
    hideContextMenu();
  };

  const handleNewFile = () => {
    setModal({ visible: true, type: "file", value: "", error: "" });
    hideContextMenu();
  };

  const handleNewFolder = () => {
    setModal({ visible: true, type: "folder", value: "", error: "" });
    hideContextMenu();
  };

  const handleModalSubmit = async () => {
    const name = modal.value.trim();
    if (!name) {
      setModal((m) => ({ ...m, error: "กรุณากรอกชื่อ" }));
      return;
    }
    if (/[/\\:*?"<>|]/.test(name)) {
      setModal((m) => ({ ...m, error: "ชื่อไฟล์/โฟลเดอร์ไม่ถูกต้อง" }));
      return;
    }
    if (modal.type === "file") {
      const filePath = `${currentDir}/${name}`;
      try {
        await invoke("write_file", { path: filePath, content: "" });
        loadDirectory(currentDir);
      } catch (error) {
        setModal((m) => ({ ...m, error: "สร้างไฟล์ไม่สำเร็จ" }));
        return;
      }
    } else if (modal.type === "folder") {
      const folderPath = `${currentDir}/${name}`;
      try {
        await invoke("create_dir", { path: folderPath });
        loadDirectory(currentDir);
      } catch (error) {
        setModal((m) => ({ ...m, error: "สร้างโฟลเดอร์ไม่สำเร็จ" }));
        return;
      }
    }
    setModal({ visible: false, type: null, value: "", error: "" });
  };

  const handleModalClose = () => {
    setModal({ visible: false, type: null, value: "", error: "" });
  };

  // Load initial directory
  useEffect(() => {
    if (tab === "files") {
      loadDirectory(currentDir);
    }
  }, [tab, currentDir]);

  // Handle click outside to close context menu
  useEffect(() => {
    const handleClickOutside = () => {
      if (contextMenu.visible) {
        hideContextMenu();
      }
    };
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, [contextMenu.visible]);

  const mm = useMemo(() => {
    const lines = content.split("\n").map((s) => s.trim());
    const title = lines.find((l) => l.startsWith("# "))?.slice(2) || "Mindmap";
    const bullets = lines
      .filter((l) => l.startsWith("- "))
      .map((l) => l.slice(2));
    return toMindmap(
      title,
      bullets.length ? bullets : ["Add - bullets in markdown"],
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
          mm,
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
          ต้นไม้
        </button>
        <button className="btn" onClick={() => setTab("graph")}>
          กราฟ
        </button>
        <button className="btn" onClick={() => setTab("files")}>
          ไฟล์
        </button>
        <button className="btn" onClick={() => setTab("settings")}>
          ตั้งค่า
        </button>
      </div>
      <div
        className="card"
        style={{ height: "calc(100% - 44px)", overflow: "auto" }}
      >
        {tab === "tree" && (
          <pre>
            • ราก{"\n"} ├─ เอกสาร{"\n"} └─ สื่อ
          </pre>
        )}
        {tab === "graph" && <div ref={containerRef} />}
        {tab === "files" && (
          <div className="file-explorer">
            <div className="file-explorer-header">
              <button className="btn btn-sm" onClick={() => setCurrentDir(".")}>
                รีเฟรช
              </button>
            </div>
            <div className="file-tree">
              {loading ? (
                <div>กำลังโหลด...</div>
              ) : (
                fileTree.map((file) => (
                  <div
                    key={file.path}
                    className={`file-item ${file.is_dir ? "directory" : "file"}`}
                    onDoubleClick={() => handleFileDoubleClick(file)}
                    onContextMenu={(e) => handleContextMenu(e, file)}
                  >
                    <span className="file-icon">
                      {file.is_dir ? "📁" : "📄"}
                    </span>
                    <span className="file-name">{file.name}</span>
                    {file.is_dir && expandedDirs.has(file.path) && (
                      <div className="file-children">
                        {/* TODO: Load subdirectory contents */}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
            {contextMenu.visible && (
              <div
                className="context-menu"
                style={{ left: contextMenu.x, top: contextMenu.y }}
                onClick={hideContextMenu}
              >
                <div className="context-menu-item" onClick={handleNewFile}>
                  ไฟล์ใหม่
                </div>
                <div className="context-menu-item" onClick={handleNewFolder}>
                  โฟลเดอร์ใหม่
                </div>
                {contextMenu.file && (
                  <>
                    <hr />
                    <div className="context-menu-item" onClick={handleDelete}>
                      ลบ
                    </div>
                  </>
                )}
              </div>
            )}
            {modal.visible && (
              <div
                className="modal-backdrop"
                style={{
                  position: "fixed",
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: "rgba(0,0,0,0.3)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  zIndex: 1000,
                }}
              >
                <div
                  className="modal"
                  style={{
                    background: "#222",
                    padding: 24,
                    borderRadius: 8,
                    minWidth: 320,
                    boxShadow: "0 2px 16px #0008",
                  }}
                >
                  <h3 style={{ marginBottom: 12 }}>
                    {modal.type === "file"
                      ? "สร้างไฟล์ใหม่"
                      : "สร้างโฟลเดอร์ใหม่"}
                  </h3>
                  <input
                    autoFocus
                    type="text"
                    value={modal.value}
                    onChange={(e) =>
                      setModal((m) => ({
                        ...m,
                        value: e.target.value,
                        error: "",
                      }))
                    }
                    placeholder={
                      modal.type === "file" ? "ชื่อไฟล์" : "ชื่อโฟลเดอร์"
                    }
                    style={{
                      width: "100%",
                      padding: "8px",
                      fontSize: "1rem",
                      marginBottom: 8,
                      borderRadius: 4,
                      border: "1px solid #444",
                      background: "#333",
                      color: "#fff",
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") handleModalSubmit();
                      if (e.key === "Escape") handleModalClose();
                    }}
                  />
                  {modal.error && (
                    <div style={{ color: "#f87171", marginBottom: 8 }}>
                      {modal.error}
                    </div>
                  )}
                  <div style={{ display: "flex", gap: 8 }}>
                    <button className="btn btn-sm" onClick={handleModalSubmit}>
                      สร้าง
                    </button>
                    <button className="btn btn-sm" onClick={handleModalClose}>
                      ยกเลิก
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        {tab === "settings" && <div>การตั้งค่าปลั๊กอิน</div>}
      </div>
    </div>
  );
}
