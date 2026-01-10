import React, { Suspense } from "react";

const VisualDashboard = React.lazy(() => import("./VisualDashboard"));

// This component is a wrapper that lazy-loads the VisualDashboard.
// This allows the main application to load without the heavy chart.js library,
// improving initial page load performance. The user will see a "Loading..."
// fallback while the component is being fetched.
export default function LazyVisualDashboard() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <VisualDashboard />
    </Suspense>
  );
}
