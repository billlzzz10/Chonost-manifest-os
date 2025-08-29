import React, { useState, useEffect } from 'react';
import { Card } from '../../packages/ui/Card';
import { Button } from '../../packages/ui/Button';
import { Typography } from '../../packages/ui/Typography';
import { Icon } from '../../packages/ui/Icon';

interface Project {
  id: string;
  name: string;
  description: string;
  documents: { id: string }[];
  characters: { id: string }[];
  updatedAt: string;
}

interface Stats {
  totalProjects: number;
  totalDocuments: number;
  totalCharacters: number;
  totalWords: number;
}

export const Dashboard: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState<Stats>({
    totalProjects: 0,
    totalDocuments: 0,
    totalCharacters: 0,
    totalWords: 0,
  });

  // Mock data for demonstration
  useEffect(() => {
    const mockProjects: Project[] = [
      {
        id: '1',
        name: 'The Chronicles of Aetheria',
        description: 'A fantasy epic about magical realms',
        documents: [{ id: '1' }, { id: '2' }],
        characters: [{ id: '1' }, { id: '2' }, { id: '3' }],
        updatedAt: new Date().toISOString(),
      },
      {
        id: '2',
        name: 'Modern Romance',
        description: 'A contemporary love story',
        documents: [{ id: '3' }],
        characters: [{ id: '4' }, { id: '5' }],
        updatedAt: new Date().toISOString(),
      },
    ];

    setProjects(mockProjects);
    setStats({
      totalProjects: mockProjects.length,
      totalDocuments: mockProjects.reduce((acc, p) => acc + p.documents.length, 0),
      totalCharacters: mockProjects.reduce((acc, p) => acc + p.characters.length, 0),
      totalWords: 15420, // Mock word count
    });
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Typography variant="h1" className="mb-2">
            Welcome to Chonost
          </Typography>
          <Typography variant="body" className="text-gray-600">
            Your creative writing companion
          </Typography>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <div className="flex items-center justify-between mb-2">
              <Typography variant="caption" className="font-medium">Projects</Typography>
              <Icon name="book" size="sm" className="text-gray-500" />
            </div>
            <Typography variant="h2" className="mb-0">{stats.totalProjects}</Typography>
          </Card>

          <Card>
            <div className="flex items-center justify-between mb-2">
              <Typography variant="caption" className="font-medium">Documents</Typography>
              <Icon name="edit" size="sm" className="text-gray-500" />
            </div>
            <Typography variant="h2" className="mb-0">{stats.totalDocuments}</Typography>
          </Card>

          <Card>
            <div className="flex items-center justify-between mb-2">
              <Typography variant="caption" className="font-medium">Characters</Typography>
              <Icon name="user" size="sm" className="text-gray-500" />
            </div>
            <Typography variant="h2" className="mb-0">{stats.totalCharacters}</Typography>
          </Card>

          <Card>
            <div className="flex items-center justify-between mb-2">
              <Typography variant="caption" className="font-medium">Total Words</Typography>
              <Icon name="save" size="sm" className="text-gray-500" />
            </div>
            <Typography variant="h2" className="mb-0">{stats.totalWords.toLocaleString()}</Typography>
          </Card>
        </div>

        {/* Projects Section */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-6">
            <Typography variant="h2">Your Projects</Typography>
            <Button>
              New Project
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <Card key={project.id} className="hover:shadow-lg transition-shadow duration-200 cursor-pointer">
                <Typography variant="h4" className="mb-2">{project.name}</Typography>
                <Typography variant="body" className="text-gray-600 mb-4">{project.description}</Typography>
                
                <div className="flex justify-between items-center mb-4">
                  <div className="flex space-x-4">
                    <span className="px-2 py-1 bg-gray-100 text-xs rounded-md">
                      {project.documents.length} docs
                    </span>
                    <span className="px-2 py-1 bg-gray-100 text-xs rounded-md">
                      {project.characters.length} characters
                    </span>
                  </div>
                </div>
                
                <Typography variant="caption" className="text-gray-500">
                  Updated {new Date(project.updatedAt).toLocaleDateString()}
                </Typography>
              </Card>
            ))}

            {/* Add New Project Card */}
            <Card className="border-dashed border-2 hover:border-blue-500 transition-colors duration-200 cursor-pointer">
              <div className="flex flex-col items-center justify-center h-48 text-gray-500">
                <Icon name="book" size="lg" className="mb-4" />
                <Typography variant="h4" className="mb-2">Create New Project</Typography>
                <Typography variant="caption">Start your next writing adventure</Typography>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

