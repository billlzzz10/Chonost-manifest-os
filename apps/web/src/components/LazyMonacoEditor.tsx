import React, { Suspense } from "react";
import type { ComponentProps } from "react";

// Lazy load the MonacoEditor component
const MonacoEditor = React.lazy(() => import("./MonacoEditor"));

type MonacoEditorProps = ComponentProps<typeof MonacoEditor>;

// This component is a wrapper that lazy-loads the MonacoEditor.
// This allows the main application to load without the heavy monaco-editor library,
// improving initial page load performance. The user will see a "Loading..."
// fallback while the component is being fetched.
export default function LazyMonacoEditor(props: MonacoEditorProps) {
  return (
    <Suspense fallback={<div>Loading Editor...</div>}>
      <MonacoEditor {...props} />
    </Suspense>
  );
}
