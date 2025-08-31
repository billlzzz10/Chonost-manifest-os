import { Request, Response } from 'express';
import { ProjectService } from '../services/project.service';

const projectService = new ProjectService();

export class ProjectController {
  async getAllProjects(req: Request, res: Response) {
    try {
      const { userId } = req.params;
      const projects = await projectService.getAllProjects(userId);
      res.json(projects);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch projects' });
    }
  }

  async getProjectById(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const project = await projectService.getProjectById(id);
      
      if (!project) {
        return res.status(404).json({ error: 'Project not found' });
      }
      
      res.json(project);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch project' });
    }
  }

  async createProject(req: Request, res: Response) {
    try {
      const project = await projectService.createProject(req.body);
      res.status(201).json(project);
    } catch (error) {
      res.status(500).json({ error: 'Failed to create project' });
    }
  }

  async updateProject(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const project = await projectService.updateProject(id, req.body);
      res.json(project);
    } catch (error) {
      res.status(500).json({ error: 'Failed to update project' });
    }
  }

  async deleteProject(req: Request, res: Response) {
    try {
      const { id } = req.params;
      await projectService.deleteProject(id);
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ error: 'Failed to delete project' });
    }
  }

  async getProjectStats(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const stats = await projectService.getProjectStats(id);
      
      if (!stats) {
        return res.status(404).json({ error: 'Project not found' });
      }
      
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch project stats' });
    }
  }
}

