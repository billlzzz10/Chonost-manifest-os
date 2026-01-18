// apps/web/src/components/LazyMonacoEditor.tsx
import React, { Suspense } from "react";

const MonacoEditor = React.lazy(() => import("./MonacoEditor"));

// Define props interface to match MonacoEditor's props
interface LazyMonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  theme?: "vs-dark" | "vs-light" | "craft-dark";
  height?: string;
}

export default function LazyMonacoEditor(props: LazyMonacoEditorProps) {
  return (
    <Suspense fallback={<div>Loading Editor...</div>}>
      <MonacoEditor {...props} />
    </Suspense>
  );
}
