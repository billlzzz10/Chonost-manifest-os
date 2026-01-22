// src/components/MonacoEditor.tsx
import { useEffect, useRef } from "react";
import { invoke } from "@tauri-apps/api/tauri";
import Editor from "@monaco-editor/react";

export interface MonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  theme?: "vs-dark" | "vs-light" | "craft-dark";
  height?: string;
}

export const MonacoEditor = ({
  value,
  onChange,
  language = "markdown",
  theme = "craft-dark",
  height = "100%",
}: MonacoEditorProps) {
  const editorRef = useRef<any>(null);

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;

    // Define custom theme that matches our glassmorphism design
    monaco.editor.defineTheme("craft-dark", {
      base: "vs-dark",
      inherit: true,
      rules: [
        { token: "comment", foreground: "9ca3af", fontStyle: "italic" },
        { token: "keyword", foreground: "6ee7b7", fontStyle: "bold" },
        { token: "string", foreground: "fbbf24" },
        { token: "number", foreground: "60a5fa" },
        { token: "type", foreground: "a78bfa" },
        { token: "function", foreground: "f472b6" },
      ],
      colors: {
        "editor.background": "#0b1322",
        "editor.foreground": "#e5e7eb",
        "editor.lineHighlightBackground": "#1f293720",
        "editor.selectionBackground": "#6ee7b730",
        "editor.inactiveSelectionBackground": "#6ee7b715",
        "editorCursor.foreground": "#6ee7b7",
        "editorLineNumber.foreground": "#6b7280",
        "editorLineNumber.activeForeground": "#9ca3af",
        "editor.findMatchBackground": "#60a5fa30",
        "editor.findMatchHighlightBackground": "#60a5fa20",
        "scrollbarSlider.background": "#374151",
        "scrollbarSlider.hoverBackground": "#4b5563",
        "scrollbarSlider.activeBackground": "#6b7280",
      },
    });

    // Set custom theme
    monaco.editor.setTheme("craft-dark");

    // Configure editor options
    editor.updateOptions({
      fontSize: 14,
      lineHeight: 1.6,
      fontFamily:
        'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace',
      minimap: { enabled: true, scale: 0.8 },
      scrollBeyondLastLine: false,
      wordWrap: "on",
      lineNumbers: "on",
      renderLineHighlight: "line",
      selectOnLineNumbers: true,
      automaticLayout: true,
      tabSize: 2,
      insertSpaces: true,
      folding: true,
      foldingStrategy: "indentation",
      showFoldingControls: "mouseover",
      bracketPairColorization: { enabled: true },
      guides: {
        bracketPairs: true,
        indentation: true,
      },
    });

    // Add custom keybindings
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, async () => {
      // Get current content from editor
      const content = editor.getValue();

      try {
        const result = await invoke('save_file', { content });
        console.log('File saved:', result);
        // You could show a success message to the user here
      } catch (error) {
        console.error('Save failed:', error);
        // You could show an error message to the user here
      }
    });

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyF, () => {
      editor.getAction("actions.find").run();
    });
  };

  const handleEditorChange = (newValue: string | undefined) => {
    if (newValue !== undefined) {
      onChange(newValue);
    }
  };

  return (
    <div className="monaco-editor-container" style={{ height }}>
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        theme={theme}
        options={{
          padding: { top: 16, bottom: 16 },
          smoothScrolling: true,
          cursorBlinking: "smooth",
          cursorSmoothCaretAnimation: "on",
          contextmenu: true,
          mouseWheelZoom: true,
          quickSuggestions: {
            other: true,
            comments: true,
            strings: true,
          },
          suggestOnTriggerCharacters: true,
          acceptSuggestionOnEnter: "on",
          tabCompletion: "on",
          wordBasedSuggestions: true,
          parameterHints: { enabled: true },
          autoClosingBrackets: "always",
          autoClosingQuotes: "always",
          autoSurround: "languageDefined",
          formatOnPaste: true,
          formatOnType: true,
        }}
      />
    </div>
  );
}
