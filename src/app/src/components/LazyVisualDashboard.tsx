import React, { Suspense } from "react";

const VisualDashboard = React.lazy(() => import("./VisualDashboard"));

// This component is a wrapper that lazy-loads the VisualDashboard.
// By using React.lazy, the VisualDashboard component and its dependencies (like chart.js)
// will be loaded in a separate chunk, reducing the initial bundle size and improving
// the application's load time. The Suspense component provides a fallback UI
// to show while the component is being loaded.
export default function LazyVisualDashboard() {
  return (
    <Suspense fallback={<div>Loading charts...</div>}>
      <VisualDashboard />
    </Suspense>
  );
}
