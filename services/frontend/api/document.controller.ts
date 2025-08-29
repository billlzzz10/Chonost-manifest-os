import { Request, Response } from 'express';
import { DocumentService } from '../services/document.service';

const documentService = new DocumentService();

export class DocumentController {
  async getAllDocuments(req: Request, res: Response) {
    try {
      const { projectId } = req.params;
      const documents = await documentService.getAllDocuments(projectId);
      res.json(documents);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch documents' });
    }
  }

  async getDocumentById(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const document = await documentService.getDocumentById(id);
      
      if (!document) {
        return res.status(404).json({ error: 'Document not found' });
      }
      
      res.json(document);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch document' });
    }
  }

  async createDocument(req: Request, res: Response) {
    try {
      const document = await documentService.createDocument(req.body);
      res.status(201).json(document);
    } catch (error) {
      res.status(500).json({ error: 'Failed to create document' });
    }
  }

  async updateDocument(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const document = await documentService.updateDocument(id, req.body);
      res.json(document);
    } catch (error) {
      res.status(500).json({ error: 'Failed to update document' });
    }
  }

  async deleteDocument(req: Request, res: Response) {
    try {
      const { id } = req.params;
      await documentService.deleteDocument(id);
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ error: 'Failed to delete document' });
    }
  }

  async getDocumentStats(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const stats = await documentService.getDocumentStats(id);
      
      if (!stats) {
        return res.status(404).json({ error: 'Document not found' });
      }
      
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch document stats' });
    }
  }

  async searchDocuments(req: Request, res: Response) {
    try {
      const { projectId } = req.params;
      const { q } = req.query;
      
      if (!q) {
        return res.status(400).json({ error: 'Query parameter is required' });
      }
      
      const documents = await documentService.searchDocuments(projectId, q as string);
      res.json(documents);
    } catch (error) {
      res.status(500).json({ error: 'Failed to search documents' });
    }
  }
}

