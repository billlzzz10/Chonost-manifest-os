import { Request, Response } from 'express';
import { CharacterService } from '../services/character.service';

const characterService = new CharacterService();

export class CharacterController {
  async getAllCharacters(req: Request, res: Response) {
    try {
      const { projectId } = req.params;
      const characters = await characterService.getAllCharacters(projectId);
      res.json(characters);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch characters' });
    }
  }

  async getCharacterById(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const character = await characterService.getCharacterById(id);
      
      if (!character) {
        return res.status(404).json({ error: 'Character not found' });
      }
      
      res.json(character);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch character' });
    }
  }

  async createCharacter(req: Request, res: Response) {
    try {
      const character = await characterService.createCharacter(req.body);
      res.status(201).json(character);
    } catch (error) {
      res.status(500).json({ error: 'Failed to create character' });
    }
  }

  async updateCharacter(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const character = await characterService.updateCharacter(id, req.body);
      res.json(character);
    } catch (error) {
      res.status(500).json({ error: 'Failed to update character' });
    }
  }

  async deleteCharacter(req: Request, res: Response) {
    try {
      const { id } = req.params;
      await characterService.deleteCharacter(id);
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ error: 'Failed to delete character' });
    }
  }

  async analyzeCharacters(req: Request, res: Response) {
    try {
      const { content, projectId } = req.body;
      const characters = await characterService.analyzeCharacterFromMarkdown(content, projectId);
      res.json(characters);
    } catch (error) {
      res.status(500).json({ error: 'Failed to analyze characters' });
    }
  }
}

