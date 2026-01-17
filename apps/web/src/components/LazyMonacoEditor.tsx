// src/components/LazyMonacoEditor.tsx
import React, { Suspense } from 'react';

const MonacoEditor = React.lazy(() => import('./MonacoEditor'));

// Create a props interface that matches the original MonacoEditor component
interface MonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  theme?: 'vs-dark' | 'vs-light' | 'craft-dark';
  height?: string;
}

const LazyMonacoEditor = (props: MonacoEditorProps) => {
  return (
    <Suspense fallback={<div style={{ height: props.height || '100%', backgroundColor: '#0b1322', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>Loading Editor...</div>}>
      <MonacoEditor {...props} />
    </Suspense>
  );
};

export default LazyMonacoEditor;
