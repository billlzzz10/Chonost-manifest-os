// MCP Service for Chonost Frontend
// เชื่อมต่อกับ MCP Orchestrator Backend

export interface MCPTool {
  name: string;
  description: string;
  category: string;
}

export interface MCPToolCall {
  tool: string;
  parameters: Record<string, any>;
}

export interface MCPToolResult {
  success: boolean;
  result?: any;
  error?: string;
  tool?: string;
  server?: string;
}

export interface MCPToolsResponse {
  tools: MCPTool[];
  source: string;
  error?: string;
}

class MCPService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = 'http://localhost:8002/api/mcp';
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('MCP Service request failed:', error);
      throw error;
    }
  }

  async getAvailableTools(): Promise<MCPToolsResponse> {
    try {
      return await this.makeRequest('/tools');
    } catch (error) {
      console.error('Failed to get MCP tools:', error);
      // Fallback to mock data
      return {
        tools: [
          {
            name: 'fs.semantic_search',
            description: 'Semantic search in codebase',
            category: 'filesystem'
          },
          {
            name: 'fs.pattern_extract',
            description: 'Extract code patterns',
            category: 'filesystem'
          },
          {
            name: 'gh.pr_create_smart',
            description: 'Create smart pull request',
            category: 'github'
          },
          {
            name: 'gh.issue_triage',
            description: 'Triage GitHub issues',
            category: 'github'
          }
        ],
        source: 'fallback',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  async callTool(toolCall: MCPToolCall): Promise<MCPToolResult> {
    try {
      const response = await this.makeRequest('/call', {
        method: 'POST',
        body: JSON.stringify(toolCall)
      });

      return {
        success: response.success || false,
        result: response.result,
        error: response.error,
        tool: response.tool,
        server: response.server
      };
    } catch (error) {
      console.error('Failed to call MCP tool:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        tool: toolCall.tool
      };
    }
  }

  // Convenience methods for specific tools
  async semanticSearch(query: string, limit: number = 5): Promise<MCPToolResult> {
    return this.callTool({
      tool: 'filesystem.semantic_search',
      parameters: { query, limit }
    });
  }

  async extractPatterns(pattern: string, filePath: string): Promise<MCPToolResult> {
    return this.callTool({
      tool: 'filesystem.pattern_extract',
      parameters: { pattern, file_path: filePath }
    });
  }

  async createSmartPR(title: string, description: string, branch: string): Promise<MCPToolResult> {
    return this.callTool({
      tool: 'gh.pr_create_smart',
      parameters: { title, description, branch }
    });
  }

  async triageIssue(issueNumber: number, action: string): Promise<MCPToolResult> {
    return this.callTool({
      tool: 'gh.issue_triage',
      parameters: { issue_number: issueNumber, action }
    });
  }

  // Get tools by category
  async getToolsByCategory(category: string): Promise<MCPTool[]> {
    try {
      const response = await this.getAvailableTools();
      return response.tools.filter(tool => tool.category === category);
    } catch (error) {
      console.error('Failed to get tools by category:', error);
      return [];
    }
  }

  // Get filesystem tools
  async getFilesystemTools(): Promise<MCPTool[]> {
    return this.getToolsByCategory('filesystem');
  }

  // Get GitHub tools
  async getGitHubTools(): Promise<MCPTool[]> {
    return this.getToolsByCategory('github');
  }
}

// Export singleton instance
export const mcpService = new MCPService();
export default mcpService;