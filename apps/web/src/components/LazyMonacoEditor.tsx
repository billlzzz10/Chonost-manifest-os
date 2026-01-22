import React, { Suspense } from "react";
import { MonacoEditorProps } from "./MonacoEditor";

const MonacoEditor = React.lazy(() => import("./MonacoEditor"));

// This component is a wrapper that lazy-loads the MonacoEditor.
// This allows the main application to load without the heavy editor library,
// improving initial page load performance. The user will see a "Loading..."
// fallback while the component is being fetched.
export default function LazyMonacoEditor(props: MonacoEditorProps) {
  return (
    <Suspense fallback={<div>Loading Editor...</div>}>
      <MonacoEditor {...props} />
    </Suspense>
  );
}
