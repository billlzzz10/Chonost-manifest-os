// MCP (Model Context Protocol) Types
// Shared between frontend and backend

export interface MCPTool {
  name: string;
  description: string;
  category: string;
  parameters?: Record<string, any>;
  returns?: any;
}

export interface MCPToolCall {
  tool: string;
  parameters: Record<string, any>;
  id?: string;
}

export interface MCPToolResult {
  success: boolean;
  data?: any;
  error?: string;
  execution_time?: number;
}

export interface MCPServer {
  id: string;
  name: string;
  version: string;
  tools: MCPTool[];
  status: 'connected' | 'disconnected' | 'error';
  last_seen?: Date;
}

export interface MCPTransportConfig {
  type: 'stdio' | 'python' | 'npx' | 'docker' | 'http';
  command?: string;
  args?: string[];
  url?: string;
  headers?: Record<string, string>;
}

export interface MCPCommonOptions {
  parallel_workers?: number;
  chunk_size?: number;
  retry_attempts?: number;
  retry_delay?: number;
  memory_limit?: number;
  cpu_limit?: number;
  progress_callback?: (progress: number) => void;
}
