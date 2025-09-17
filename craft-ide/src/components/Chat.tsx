import React, { useState } from 'react';

// [NOTE: Styles are omitted for brevity as they are unchanged]
const style: React.CSSProperties = { flex: 1, borderBottom: '1px solid #ccc', padding: '10px', overflow: 'auto', display: 'flex', flexDirection: 'column' };
const messagesStyle: React.CSSProperties = { flexGrow: 1, marginBottom: '10px', border: '1px solid #eee', padding: '5px', backgroundColor: 'white' };
const inputContainerStyle: React.CSSProperties = { display: 'flex', gap: '5px' };

const MCP_SERVER_URL = 'http://localhost:3001';

const logRun = (logEntry: any) => {
    fetch(`${MCP_SERVER_URL}/runlog/put`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logEntry),
    }).catch(console.error); // Fire-and-forget logging
};

export const Chat: React.FC = () => {
    const [messages, setMessages] = useState([{ "from": "AI", "text": "Hello! How can I help you?" }]);
    const [toolOutput, setToolOutput] = useState('');

    const handleToolSelection = async (event: React.ChangeEvent<HTMLSelectElement>) => {
        const selectedToolName = event.target.value;
        if (!selectedToolName) return;

        event.target.value = ""; // Reset dropdown

        let endpoint = '';
        let body = {};
        let toolIdentifier = '';

        if (selectedToolName === 'segment') {
            toolIdentifier = 'document-segmentation';
            endpoint = '/seg/run';
            body = { docHash: 'current-doc-hash' };
        } else if (selectedToolName === 'index') {
            toolIdentifier = 'code-reference-indexer';
            endpoint = '/code-index/run';
            body = { paths: ['/src/components', '/src/services'] };
        }

        setToolOutput(`Running ${toolIdentifier}...`);
        const startTime = Date.now();
        try {
            const response = await fetch(`${MCP_SERVER_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const data = await response.json();
            const latency_ms = Date.now() - startTime;
            if (!response.ok) {
                logRun({ phase: 'error', tool: toolIdentifier, status: 'failed', latency_ms });
                throw new Error(data.error || 'API call failed');
            }
            logRun({ phase: 'tool', tool: toolIdentifier, status: 'success', latency_ms });
            setToolOutput(JSON.stringify(data, null, 2));
        } catch (error) {
            const latency_ms = Date.now() - startTime;
            logRun({ phase: 'error', tool: toolIdentifier, status: 'failed', latency_ms });
            const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
            setToolOutput(`Error: ${errorMessage}`);
        }
    }

  return (
    <div style={style}>
      <h2>Chat Panel</h2>
      <div style={messagesStyle}>
        {messages.map((msg, index) => (
            <p key={index}><strong>{msg.from}:</strong> {msg.text}</p>
        ))}
        {toolOutput && <pre style={{backgroundColor: '#eee', padding: '5px'}}><strong>Tool Output:</strong><br/>{toolOutput}</pre>}
      </div>
      <div style={inputContainerStyle}>
        <input type="text" placeholder="Type a message..." style={{flexGrow: 1}} />
        <select onChange={handleToolSelection} defaultValue="">
            <option value="" disabled>Use Tool</option>
            <option value="segment">Segment current doc</option>
            <option value="index">Index code refs</option>
        </select>
      </div>
    </div>
  );
};
