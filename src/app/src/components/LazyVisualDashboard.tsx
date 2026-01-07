import React, { lazy, Suspense } from "react";

// Lazily import the VisualDashboard component
const VisualDashboard = lazy(() => import("./VisualDashboard"));

// This component centralizes the lazy loading and Suspense fallback for VisualDashboard.
// By using this component, we ensure the chart.js library is code-split consistently
// and avoid duplicating the lazy-loading logic in multiple places.
export default function LazyVisualDashboard() {
  return (
    <Suspense fallback={<div>Loading charts...</div>}>
      <VisualDashboard />
    </Suspense>
  );
}
