import React, { Suspense } from 'react';

// ⚡ Bolt: Lazy load the VisualDashboard component.
// This is a performance optimization that splits the large chart.js library
// (a dependency of VisualDashboard) into a separate chunk, reducing the
// initial bundle size and improving the app's load time.
const VisualDashboard = React.lazy(() => import('./VisualDashboard'));

// ⚡ Bolt: Create a wrapper component for the lazy-loaded dashboard.
// This component centralizes the lazy-loading logic and the Suspense
// boundary. By using this component, we avoid duplicating the lazy-loading
// code and ensure a consistent fallback UI wherever the dashboard is used.
export default function LazyVisualDashboard() {
  return (
    <Suspense fallback={<div>Loading dashboard...</div>}>
      <VisualDashboard />
    </Suspense>
  );
}
