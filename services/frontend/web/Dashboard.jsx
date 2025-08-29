import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BookOpen, Users, FileText, Plus, BarChart3 } from 'lucide-react';

const Dashboard = () => {
  const [projects, setProjects] = useState([]);
  const [stats, setStats] = useState({
    totalProjects: 0,
    totalDocuments: 0,
    totalCharacters: 0,
    totalWords: 0,
  });

  // Mock data for demonstration
  useEffect(() => {
    const mockProjects = [
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
          <h1 className="text-4xl font-medium text-gray-800 mb-2">
            Welcome to Chonost
          </h1>
          <p className="text-lg text-gray-600">
            Your creative writing companion
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Projects</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalProjects}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Documents</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalDocuments}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Characters</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalCharacters}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Words</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalWords.toLocaleString()}</div>
            </CardContent>
          </Card>
        </div>

        {/* Projects Section */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-medium text-gray-800">Your Projects</h2>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Project
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <Card key={project.id} className="hover:shadow-lg transition-shadow duration-200 cursor-pointer">
                <CardHeader>
                  <CardTitle className="text-lg">{project.name}</CardTitle>
                  <CardDescription>{project.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-between items-center mb-4">
                    <div className="flex space-x-4">
                      <Badge variant="secondary">
                        {project.documents.length} docs
                      </Badge>
                      <Badge variant="secondary">
                        {project.characters.length} characters
                      </Badge>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">
                    Updated {new Date(project.updatedAt).toLocaleDateString()}
                  </div>
                </CardContent>
              </Card>
            ))}

            {/* Add New Project Card */}
            <Card className="border-dashed border-2 hover:border-blue-500 transition-colors duration-200 cursor-pointer">
              <CardContent className="flex flex-col items-center justify-center h-48 text-gray-500">
                <Plus className="h-12 w-12 mb-4" />
                <p className="text-lg font-medium">Create New Project</p>
                <p className="text-sm">Start your next writing adventure</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

