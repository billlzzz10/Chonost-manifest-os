import React, { Suspense } from 'react';
import './LazyMonacoEditor.css';

// Lazily load Monaco Editor to reduce the main bundle size and improve initial page load time.
import type { MonacoEditorProps } from './MonacoEditor';
const MonacoEditor = React.lazy(() => import('./MonacoEditor'));

// A skeleton loader that mimics the editor's appearance to prevent layout shift.
const EditorLoadingSkeleton = () => (
  <div className="editor-loading-skeleton">
    <div>
      Loading Editor...
    </div>
  </div>
);

// The lazy-loaded Monaco Editor component with proper typing.
const LazyMonacoEditor = (props: MonacoEditorProps) => {
  return (
    <Suspense fallback={<EditorLoadingSkeleton />}>
      <MonacoEditor {...props} />
    </Suspense>
  );
};

export default LazyMonacoEditor;
