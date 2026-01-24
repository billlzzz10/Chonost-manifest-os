import React, { Suspense } from "react";

const MonacoEditor = React.lazy(() => import("./MonacoEditor"));

interface LazyMonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  theme?: "vs-dark" | "vs-light" | "craft-dark";
  height?: string;
}

// This component is a wrapper that lazy-loads the MonacoEditor.
// This allows the main application to load without the heavy monaco-editor library,
// improving initial page load performance. The user will see a "Loading..."
// fallback while the component is being fetched.
export default function LazyMonacoEditor(props: LazyMonacoEditorProps) {
  return (
    <Suspense fallback={<div className="loading-editor">Loading Editor...</div>}>
      <MonacoEditor {...props} />
    </Suspense>
  );
}
