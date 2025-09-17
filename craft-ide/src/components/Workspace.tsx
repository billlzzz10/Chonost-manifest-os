import React from 'react';
import { Editor } from './Editor';
import { Whiteboard } from './Whiteboard';
import { Chat } from './Chat';
import { Console } from './Console';

const containerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'row',
  height: '100vh',
  width: '100vw',
  fontFamily: 'sans-serif',
};

const mainPanelStyle: React.CSSProperties = {
  flex: 3,
  display: 'flex',
  flexDirection: 'column',
};

const rightPanelStyle: React.CSSProperties = {
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  borderLeft: '1px solid #ccc',
};

export const Workspace: React.FC = () => {
  return (
    <div style={containerStyle}>
      <div style={mainPanelStyle}>
        <Editor />
        <Whiteboard />
      </div>
      <div style={rightPanelStyle}>
        <Chat />
        <Console />
      </div>
    </div>
  );
};
