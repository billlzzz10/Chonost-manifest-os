import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export interface CreateProjectDto {
  name: string;
  description?: string;
  userId: string;
}

export interface UpdateProjectDto {
  name?: string;
  description?: string;
}

export class ProjectService {
  async getAllProjects(userId: string) {
    return await prisma.project.findMany({
      where: { userId },
      include: {
        documents: true,
        characters: true,
        user: true,
      },
      orderBy: {
        updatedAt: 'desc',
      },
    });
  }

  async getProjectById(id: string) {
    return await prisma.project.findUnique({
      where: { id },
      include: {
        documents: true,
        characters: true,
        user: true,
      },
    });
  }

  async createProject(data: CreateProjectDto) {
    return await prisma.project.create({
      data,
      include: {
        documents: true,
        characters: true,
        user: true,
      },
    });
  }

  async updateProject(id: string, data: UpdateProjectDto) {
    return await prisma.project.update({
      where: { id },
      data,
      include: {
        documents: true,
        characters: true,
        user: true,
      },
    });
  }

  async deleteProject(id: string) {
    return await prisma.project.delete({
      where: { id },
    });
  }

  async getProjectStats(id: string) {
    const project = await this.getProjectById(id);
    if (!project) return null;

    const totalWords = project.documents.reduce((total, doc) => {
      return total + (doc.content.split(' ').length || 0);
    }, 0);

    const totalCharacters = project.documents.reduce((total, doc) => {
      return total + doc.content.length;
    }, 0);

    return {
      ...project,
      stats: {
        totalDocuments: project.documents.length,
        totalCharacters: project.characters.length,
        totalWords,
        totalCharactersCount: totalCharacters,
      },
    };
  }
}

