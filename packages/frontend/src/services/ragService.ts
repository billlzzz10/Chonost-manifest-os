// RAG Service for Chonost Frontend
// เชื่อมต่อกับ Local RAG Service

export interface RAGDocument {
  id: number;
  title: string;
  type: string;
  chunks: number;
  updated_at: string;
}

export interface RAGSearchResult {
  file_path: string;
  title: string;
  content: string;
  chunk_index: number;
  similarity: number;
}

export interface RAGInfo {
  total_documents: number;
  total_chunks: number;
  documents: Record<string, RAGDocument>;
}

class RAGService {
  private baseUrl: string;

  constructor() {
    // เชื่อมต่อกับ Local RAG API
    this.baseUrl = 'http://localhost:8000/api/rag';
  }

  // Real implementation methods
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
      console.error('RAG Service request failed:', error);
      throw error;
    }
  }

  async getDocumentInfo(): Promise<RAGInfo> {
    try {
      return await this.makeRequest('/info');
    } catch (error) {
      console.error('Failed to get document info:', error);
      // Fallback to mock data
      return this.getMockDocumentInfo();
    }
  }

  async search(query: string, limit: number = 5): Promise<RAGSearchResult[]> {
    try {
      const params = new URLSearchParams({ query, limit: limit.toString() });
      return await this.makeRequest(`/search?${params}`);
    } catch (error) {
      console.error('Failed to search documents:', error);
      // Fallback to mock data
      return this.getMockSearchResults(query, limit);
    }
  }

  async addDocument(filePath: string, content: string, title?: string, type: string = "text"): Promise<boolean> {
    try {
      const response = await this.makeRequest('/documents', {
        method: 'POST',
        body: JSON.stringify({
          file_path: filePath,
          content: content,
          title: title || filePath,
          type: type
        })
      });
      return response.message === 'Document added successfully';
    } catch (error) {
      console.error('Failed to add document:', error);
      return false;
    }
  }

  async deleteDocument(filePath: string): Promise<boolean> {
    try {
      const response = await this.makeRequest(`/documents/${encodeURIComponent(filePath)}`, {
        method: 'DELETE'
      });
      return response.message === 'Document deleted successfully';
    } catch (error) {
      console.error('Failed to delete document:', error);
      return false;
    }
  }

  async getDocuments(): Promise<RAGDocument[]> {
    try {
      return await this.makeRequest('/documents');
    } catch (error) {
      console.error('Failed to get documents:', error);
      // Fallback to mock data
      return this.getMockDocuments();
    }
  }

  async addSampleDocuments(): Promise<boolean> {
    try {
      const response = await this.makeRequest('/test/add-sample', {
        method: 'POST'
      });
      console.log('Sample documents added:', response);
      return true;
    } catch (error) {
      console.error('Failed to add sample documents:', error);
      return false;
    }
  }

  // Mock data fallback methods
  private getMockDocumentInfo(): RAGInfo {
    return {
      total_documents: 3,
      total_chunks: 35,
      documents: {
        'doc_1.md': {
          id: 1,
          title: "Chonost Development Roadmap",
          type: "markdown",
          chunks: 15,
          updated_at: "2025-09-01T03:11:59.519347"
        },
        'doc_2.md': {
          id: 2,
          title: "The Trinity Layout Design",
          type: "markdown",
          chunks: 8,
          updated_at: "2025-09-01T03:10:30.123456"
        },
        'doc_3.md': {
          id: 3,
          title: "AI Integration Guide",
          type: "markdown",
          chunks: 12,
          updated_at: "2025-09-01T03:09:15.789012"
        }
      }
    };
  }

  private getMockDocuments(): RAGDocument[] {
    return [
      {
        id: 1,
        title: "Chonost Development Roadmap",
        type: "markdown",
        chunks: 15,
        updated_at: "2025-09-01T03:11:59.519347"
      },
      {
        id: 2,
        title: "The Trinity Layout Design",
        type: "markdown",
        chunks: 8,
        updated_at: "2025-09-01T03:10:30.123456"
      },
      {
        id: 3,
        title: "AI Integration Guide",
        type: "markdown",
        chunks: 12,
        updated_at: "2025-09-01T03:09:15.789012"
      }
    ];
  }

  private getMockSearchResults(query: string, limit: number): RAGSearchResult[] {
    const mockResults: RAGSearchResult[] = [
      {
        file_path: "DEVELOPMENT_ROADMAP.md",
        title: "Chonost Development Roadmap",
        content: "Phase 2: Advanced AI & Background Services - The All-Seeing Eye for file indexing...",
        chunk_index: 0,
        similarity: 0.95
      },
      {
        file_path: "The Trinity Layout Design.md",
        title: "The Trinity Layout Design",
        content: "The Trinity Layout consists of three main areas: Left Sidebar (Knowledge Explorer)...",
        chunk_index: 1,
        similarity: 0.87
      }
    ];

    // Filter based on query
    const filteredResults = mockResults.filter(result =>
      result.content.toLowerCase().includes(query.toLowerCase()) ||
      result.title.toLowerCase().includes(query.toLowerCase())
    );
    
    return filteredResults.slice(0, limit);
  }
}

// Export singleton instance
export const ragService = new RAGService();
export default ragService;
