import express from 'express';
import cors from 'cors';
import { CharacterController } from './controllers/character.controller';
import { ProjectController } from './controllers/project.controller';
import { DocumentController } from './controllers/document.controller';

const app = express();
const port = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Controllers
const characterController = new CharacterController();
const projectController = new ProjectController();
const documentController = new DocumentController();

// Routes
// Project routes
app.get('/api/users/:userId/projects', projectController.getAllProjects);
app.get('/api/projects/:id', projectController.getProjectById);
app.post('/api/projects', projectController.createProject);
app.put('/api/projects/:id', projectController.updateProject);
app.delete('/api/projects/:id', projectController.deleteProject);
app.get('/api/projects/:id/stats', projectController.getProjectStats);

// Document routes
app.get('/api/projects/:projectId/documents', documentController.getAllDocuments);
app.get('/api/documents/:id', documentController.getDocumentById);
app.post('/api/documents', documentController.createDocument);
app.put('/api/documents/:id', documentController.updateDocument);
app.delete('/api/documents/:id', documentController.deleteDocument);
app.get('/api/documents/:id/stats', documentController.getDocumentStats);
app.get('/api/projects/:projectId/documents/search', documentController.searchDocuments);

// Character routes
app.get('/api/projects/:projectId/characters', characterController.getAllCharacters);
app.get('/api/characters/:id', characterController.getCharacterById);
app.post('/api/characters', characterController.createCharacter);
app.put('/api/characters/:id', characterController.updateCharacter);
app.delete('/api/characters/:id', characterController.deleteCharacter);
app.post('/api/characters/analyze', characterController.analyzeCharacters);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'Chonost API is running' });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Chonost API server running on port ${port}`);
});

export default app;

