import { PrismaClient } from '@prisma/client';
import { CharacterService } from './character.service';

const prisma = new PrismaClient();
const characterService = new CharacterService();

export interface CreateDocumentDto {
  title: string;
  content: string;
  projectId: string;
}

export interface UpdateDocumentDto {
  title?: string;
  content?: string;
}

export class DocumentService {
  async getAllDocuments(projectId: string) {
    return await prisma.document.findMany({
      where: { projectId },
      include: {
        project: true,
      },
      orderBy: {
        updatedAt: 'desc',
      },
    });
  }

  async getDocumentById(id: string) {
    return await prisma.document.findUnique({
      where: { id },
      include: {
        project: true,
      },
    });
  }

  async createDocument(data: CreateDocumentDto) {
    const document = await prisma.document.create({
      data,
      include: {
        project: true,
      },
    });

    // Auto-analyze characters from content
    if (data.content) {
      await characterService.analyzeCharacterFromMarkdown(data.content, data.projectId);
    }

    return document;
  }

  async updateDocument(id: string, data: UpdateDocumentDto) {
    const document = await prisma.document.update({
      where: { id },
      data,
      include: {
        project: true,
      },
    });

    // Re-analyze characters if content changed
    if (data.content) {
      await characterService.analyzeCharacterFromMarkdown(data.content, document.projectId);
    }

    return document;
  }

  async deleteDocument(id: string) {
    return await prisma.document.delete({
      where: { id },
    });
  }

  async getDocumentStats(id: string) {
    const document = await this.getDocumentById(id);
    if (!document) return null;

    const wordCount = document.content.split(' ').filter(word => word.length > 0).length;
    const characterCount = document.content.length;
    const paragraphCount = document.content.split('\n\n').filter(p => p.trim().length > 0).length;

    return {
      ...document,
      stats: {
        wordCount,
        characterCount,
        paragraphCount,
        readingTime: Math.ceil(wordCount / 200), // Assuming 200 words per minute
      },
    };
  }

  async searchDocuments(projectId: string, query: string) {
    return await prisma.document.findMany({
      where: {
        projectId,
        OR: [
          {
            title: {
              contains: query,
              mode: 'insensitive',
            },
          },
          {
            content: {
              contains: query,
              mode: 'insensitive',
            },
          },
        ],
      },
      include: {
        project: true,
      },
      orderBy: {
        updatedAt: 'desc',
      },
    });
  }
}

