import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export interface CreateCharacterDto {
  name: string;
  description?: string;
  projectId: string;
}

export interface UpdateCharacterDto {
  name?: string;
  description?: string;
}

export class CharacterService {
  async getAllCharacters(projectId: string) {
    return await prisma.character.findMany({
      where: { projectId },
      include: {
        project: true,
      },
      orderBy: {
        createdAt: 'desc',
      },
    });
  }

  async getCharacterById(id: string) {
    return await prisma.character.findUnique({
      where: { id },
      include: {
        project: true,
      },
    });
  }

  async createCharacter(data: CreateCharacterDto) {
    return await prisma.character.create({
      data,
      include: {
        project: true,
      },
    });
  }

  async updateCharacter(id: string, data: UpdateCharacterDto) {
    return await prisma.character.update({
      where: { id },
      data,
      include: {
        project: true,
      },
    });
  }

  async deleteCharacter(id: string) {
    return await prisma.character.delete({
      where: { id },
    });
  }

  async analyzeCharacterFromMarkdown(content: string, projectId: string) {
    // Simple character extraction from markdown content
    const characterNames = this.extractCharacterNames(content);
    const characters = [];

    for (const name of characterNames) {
      const existingCharacter = await prisma.character.findFirst({
        where: {
          name,
          projectId,
        },
      });

      if (!existingCharacter) {
        const character = await this.createCharacter({
          name,
          description: `Character automatically detected from document`,
          projectId,
        });
        characters.push(character);
      }
    }

    return characters;
  }

  private extractCharacterNames(content: string): string[] {
    // Simple regex to find potential character names (capitalized words)
    const namePattern = /\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g;
    const matches = content.match(namePattern) || [];
    
    // Filter out common words and duplicates
    const commonWords = ['The', 'This', 'That', 'Chapter', 'Section', 'Part'];
    const uniqueNames = [...new Set(matches)]
      .filter(name => !commonWords.includes(name))
      .filter(name => name.length > 2);

    return uniqueNames;
  }
}

