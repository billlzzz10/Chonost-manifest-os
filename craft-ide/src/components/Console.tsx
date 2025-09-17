import React, { useState } from 'react';

// [NOTE: Styles are omitted for brevity as they are unchanged]
const style: React.CSSProperties = { flex: 2, padding: '10px', display: 'flex', flexDirection: 'column', backgroundColor: '#f5f5f5', overflow: 'auto' };
const tabsStyle: React.CSSProperties = { display: 'flex', borderBottom: '1px solid #ccc', flexShrink: 0 };
const tabStyle: React.CSSProperties = { padding: '5px 10px', cursor: 'pointer' };
const activeTabStyle: React.CSSProperties = { ...tabStyle, borderBottom: '2px solid blue', fontWeight: 'bold' };
const contentStyle: React.CSSProperties = { flexGrow: 1, marginTop: '10px', padding: '5px', border: '1px solid #eee', backgroundColor: 'white', overflow: 'auto', whiteSpace: 'pre-wrap', wordBreak: 'break-all' };
const buttonStyle: React.CSSProperties = { margin: '2px', padding: '5px', cursor: 'pointer' };
const tableStyle: React.CSSProperties = { width: '100%', borderCollapse: 'collapse', marginTop: '10px' };
const thStyle: React.CSSProperties = { border: '1px solid #ddd', padding: '8px', backgroundColor: '#f2f2f2', textAlign: 'left' };
const tdStyle: React.CSSProperties = { border: '1px solid #ddd', padding: '8px' };


const MCP_SERVER_URL = 'http://localhost:3001';

const logRun = (logEntry: any) => {
    fetch(`${MCP_SERVER_URL}/runlog/put`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logEntry),
    }).catch(console.error); // Fire-and-forget logging
};

export const Console: React.FC = () => {
  const [activeTab, setActiveTab] = useState('Tools');
  const [output, setOutput] = useState('Tool output will appear here.');

  const runTool = async (toolName: string, args: any = {}) => {
    setOutput(`Running tool: ${toolName}...`);
    setActiveTab('Output');
    const startTime = Date.now();
    try {
      const response = await fetch(`${MCP_SERVER_URL}/mcp/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool: toolName, args }),
      });
      const data = await response.json();
      const latency_ms = Date.now() - startTime;
      if (!response.ok) {
        logRun({ phase: 'error', tool: toolName, status: 'failed', latency_ms });
        throw new Error(data.error || 'API call failed');
      }
      logRun({ phase: 'tool', tool: toolName, status: 'success', latency_ms });
      setOutput(JSON.stringify(data, null, 2));
    } catch (error) {
      const latency_ms = Date.now() - startTime;
      logRun({ phase: 'error', tool: toolName, status: 'failed', latency_ms });
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
      setOutput(`Error: ${errorMessage}`);
    }
  };

  const tools = ['filesystem', 'fetch', 'github-downloader', 'command-executor'];

  return (
    <div style={style}>
      <h2>Console</h2>
      <div style={tabsStyle}>
        <div style={activeTab === 'Dashboard' ? activeTabStyle : tabStyle} onClick={() => setActiveTab('Dashboard')}>Dashboard</div>
        <div style={activeTab === 'Tools' ? activeTabStyle : tabStyle} onClick={() => setActiveTab('Tools')}>Tools</div>
        <div style={activeTab === 'Output' ? activeTabStyle : tabStyle} onClick={() => setActiveTab('Output')}>Output</div>
      </div>
      <div style={contentStyle}>
        {activeTab === 'Dashboard' && (
            <div>
                <h4>Metrics Dashboard</h4>
                {/* Placeholder UI from previous step */}
                <div style={{marginBottom: '20px'}}><strong>Cache Stats (Hits/Misses)</strong><div style={{display: 'flex', alignItems: 'flex-end', height: '100px', border: '1px solid #ccc', padding: '5px'}}><div style={{width: '50px', backgroundColor: 'green', height: '80%'}} title="Hits"></div><div style={{width: '50px', backgroundColor: 'red', height: '20%'}} title="Misses"></div></div></div>
                <div style={{marginBottom: '20px'}}><strong>Token Usage (In/Out)</strong><div style={{display: 'flex', alignItems: 'flex-end', height: '100px', border: '1px solid #ccc', padding: '5px'}}><div style={{width: '50px', backgroundColor: 'blue', height: '60%'}} title="Tokens In"></div><div style={{width: '50px', backgroundColor: 'orange', height: '90%'}} title="Tokens Out"></div></div></div>
                <h4>Run Logs</h4>
                <table style={tableStyle}><thead><tr><th style={thStyle}>phase</th><th style={thStyle}>tool</th><th style={thStyle}>status</th><th style={thStyle}>latency_ms</th></tr></thead><tbody><tr><td style={tdStyle}>tool</td><td style={tdStyle}>fetch</td><td style={tdStyle}>success</td><td style={tdStyle}>120</td></tr><tr><td style={tdStyle}>error</td><td style={tdStyle}>filesystem</td><td style={tdStyle}>failed</td><td style={tdStyle}>55</td></tr></tbody></table>
            </div>
        )}
        {activeTab === 'Tools' && (
            <div>
                <h4>MCP Tools</h4>
                {tools.map(tool => (
                    <button key={tool} style={buttonStyle} onClick={() => runTool(tool)}>
                        Run {tool}
                    </button>
                ))}
            </div>
        )}
        {activeTab === 'Output' && <pre>{output}</pre>}
      </div>
    </div>
  );
};
