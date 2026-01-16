import React, { Suspense } from "react";

const MonacoEditor = React.lazy(() => import("./MonacoEditor"));

// This component is a wrapper that lazy-loads the MonacoEditor.
// This allows the main application to load without the heavy @monaco-editor/react library,
// improving initial page load performance. The user will see a "Loading editor..."
// fallback while the component is being fetched.
export default function LazyMonacoEditor(props: React.ComponentProps<typeof MonacoEditor>) {
  return (
    <Suspense fallback={<div>Loading editor...</div>}>
      <MonacoEditor {...props} />
    </Suspense>
  );
}
