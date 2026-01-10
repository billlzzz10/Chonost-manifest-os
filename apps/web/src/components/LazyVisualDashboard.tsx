import React, { Suspense } from 'react';

const VisualDashboard = React.lazy(() => import('./VisualDashboard'));

export default function LazyVisualDashboard() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <VisualDashboard />
    </Suspense>
  );
}
