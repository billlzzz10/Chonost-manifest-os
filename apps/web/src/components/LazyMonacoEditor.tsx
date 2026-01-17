import React, { Suspense } from "react";

// Performance Optimization: Lazy load the Monaco Editor.
// The @monaco-editor/react library is large and not needed on initial page load.
// By lazy-loading it, we reduce the initial bundle size, leading to a faster
// Time to Interactive (TTI). The user will see a simple "Loading Editor..."
// fallback while the editor component is fetched on demand.
const MonacoEditor = React.lazy(() => import("./MonacoEditor"));

interface MonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  theme?: "vs-dark" | "vs-light" | "craft-dark";
  height?: string;
}

export default function LazyMonacoEditor(props: MonacoEditorProps) {
  return (
    <Suspense fallback={<div>Loading Editor...</div>}>
      <MonacoEditor {...props} />
    </Suspense>
  );
}
