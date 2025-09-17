import React from 'react';

const style: React.CSSProperties = {
  flex: 1,
  padding: '10px',
  overflow: 'auto',
  backgroundColor: '#f5f5f5',
};

export const Whiteboard: React.FC = () => {
  return (
    <div style={style}>
      <h2>Whiteboard Panel</h2>
      <p>This is the whiteboard area.</p>
    </div>
  );
};
