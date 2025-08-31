import { ragService } from './ragService';

export interface KnowledgeNode {
  id: string;
  title: string;
  type: 'document' | 'character' | 'location' | 'concept' | 'note';
  children?: KnowledgeNode[];
  isExpanded?: boolean;
  content?: string;
  metadata?: any;
}

export interface SearchResult {
  id: string;
  title: string;
  content: string;
  score: number;
  type: string;
}

class KnowledgeService {
  private baseUrl = 'http://localhost:8000/api';

  async getDocuments(): Promise<KnowledgeNode[]> {
    try {
      const response = await fetch(`${this.baseUrl}/rag/info`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      const documents = data.documents || {};
      
      return Object.entries(documents).map(([filePath, doc]: [string, any]) => ({
        id: doc.id?.toString() || filePath,
        title: doc.title || filePath,
        type: 'document' as const,
        content: doc.content || '',
        metadata: {
          file_path: filePath,
          chunks: doc.chunks || 0,
          updated_at: doc.updated_at
        }
      }));
    } catch (error) {
      console.error('Error fetching documents:', error);
      // Fallback to mock data
      return [
        {
          id: '1',
          title: 'Chonost Development Roadmap',
          type: 'document',
          content: 'Development roadmap for Chonost ecosystem...',
          metadata: { chunks: 15, updated_at: new Date().toISOString() }
        },
        {
          id: '2',
          title: 'The Trinity Layout Design',
          type: 'document',
          content: 'Design specifications for The Trinity Layout...',
          metadata: { chunks: 8, updated_at: new Date().toISOString() }
        },
        {
          id: '3',
          title: 'AI Integration Guide',
          type: 'document',
          content: 'Guide for integrating AI services...',
          metadata: { chunks: 12, updated_at: new Date().toISOString() }
        }
      ];
    }
  }

  async searchKnowledge(query: string, limit: number = 5): Promise<SearchResult[]> {
    try {
      const response = await fetch(`${this.baseUrl}/rag/search?query=${encodeURIComponent(query)}&limit=${limit}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const results = await response.json();
      return results.map((result: any) => ({
        id: result.id || result.chunk_id,
        title: result.title || result.document_title || 'Untitled',
        content: result.content || result.text || '',
        score: result.score || 0,
        type: result.type || 'document'
      }));
    } catch (error) {
      console.error('Error searching knowledge:', error);
      // Fallback to mock results
      return [
        {
          id: '1',
          title: 'Trinity Layout',
          content: 'The Trinity Layout consists of three main panels...',
          score: 0.95,
          type: 'document'
        }
      ];
    }
  }

  async getKnowledgeGraph(): Promise<KnowledgeNode[]> {
    try {
      const documents = await this.getDocuments();
      
      return [
        {
          id: 'documents',
          title: 'Documents',
          type: 'document',
          isExpanded: true,
          children: documents
        },
        {
          id: 'characters',
          title: 'Characters',
          type: 'character',
          isExpanded: false,
          children: [
            { id: 'char1', title: 'John Smith', type: 'character' },
            { id: 'char2', title: 'Mary Johnson', type: 'character' },
          ]
        },
        {
          id: 'locations',
          title: 'Locations',
          type: 'location',
          isExpanded: false,
          children: [
            { id: 'loc1', title: 'New York', type: 'location' },
            { id: 'loc2', title: 'London', type: 'location' },
          ]
        },
        {
          id: 'concepts',
          title: 'Concepts',
          type: 'concept',
          isExpanded: false,
          children: [
            { id: 'concept1', title: 'Love', type: 'concept' },
            { id: 'concept2', title: 'Betrayal', type: 'concept' },
          ]
        }
      ];
    } catch (error) {
      console.error('Error building knowledge graph:', error);
      return [];
    }
  }

  async addDocument(title: string, content: string, filePath?: string): Promise<KnowledgeNode> {
    try {
      const response = await fetch(`${this.baseUrl}/rag/documents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          content,
          file_path: filePath || `${title.toLowerCase().replace(/\s+/g, '_')}.md`,
          type: 'markdown'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return {
        id: result.id?.toString() || Date.now().toString(),
        title,
        type: 'document',
        content,
        metadata: { file_path: filePath }
      };
    } catch (error) {
      console.error('Error adding document:', error);
      throw error;
    }
  }
}

export const knowledgeService = new KnowledgeService();
