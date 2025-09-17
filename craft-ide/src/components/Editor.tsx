import React from 'react';

const style: React.CSSProperties = {
  flex: 2,
  borderBottom: '1px solid #ccc',
  padding: '10px',
  overflow: 'auto',
};

export const Editor: React.FC = () => {
  return (
    <div style={style}>
      <h2>Editor Panel</h2>
      <textarea
        defaultValue="Start typing your document here..."
        style={{ width: '95%', height: '80%', fontFamily: 'monospace' }}
      />
    </div>
  );
};
