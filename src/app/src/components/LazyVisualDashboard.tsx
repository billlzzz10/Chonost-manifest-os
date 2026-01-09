import React, { Suspense } from 'react';

const VisualDashboard = React.lazy(() => import('./VisualDashboard'));

export default function LazyVisualDashboard() {
  return (
    <Suspense fallback={<div>Loading dashboard...</div>}>
      <VisualDashboard />
    </Suspense>
  );
}
