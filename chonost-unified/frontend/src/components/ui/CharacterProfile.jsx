import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { User, Plus, Edit, Trash2, Users, BookOpen } from 'lucide-react';

const CharacterCard = ({ character, onEdit, onDelete }) => {
  return (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <CardTitle className="text-lg">{character.name}</CardTitle>
              <CardDescription>
                {character.appearances} appearances
              </CardDescription>
            </div>
          </div>
          <div className="flex space-x-2">
            <Button variant="ghost" size="sm" onClick={() => onEdit(character)}>
              <Edit className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => onDelete(character.id)}>
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {character.description && (
          <p className="text-gray-600 mb-4 line-clamp-3">
            {character.description}
          </p>
        )}

        {character.relationships && character.relationships.length > 0 && (
          <div className="mb-4">
            <p className="text-sm font-medium text-gray-700 mb-2">Relationships:</p>
            <div className="flex flex-wrap gap-1">
              {character.relationships.slice(0, 3).map((rel, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {rel}
                </Badge>
              ))}
              {character.relationships.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{character.relationships.length - 3} more
                </Badge>
              )}
            </div>
          </div>
        )}

        <div className="flex justify-between items-center text-sm text-gray-500">
          <span>Created {new Date(character.createdAt).toLocaleDateString()}</span>
          <Badge variant="outline">{character.project?.name}</Badge>
        </div>
      </CardContent>
    </Card>
  );
};

const CharacterProfile = () => {
  const [characters, setCharacters] = useState([]);
  const [isAddingCharacter, setIsAddingCharacter] = useState(false);
  const [editingCharacter, setEditingCharacter] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    relationships: '',
  });

  // Mock data
  useEffect(() => {
    const mockCharacters = [
      {
        id: '1',
        name: 'Aria Moonwhisper',
        description: 'A young elven mage with the power to control moonlight. She is brave but sometimes reckless, always putting others before herself.',
        appearances: 15,
        relationships: ['Theron Stormwind', 'Elder Silvana', 'Shadow Wolf'],
        createdAt: new Date().toISOString(),
        project: { name: 'The Chronicles of Aetheria' },
      },
      {
        id: '2',
        name: 'Theron Stormwind',
        description: 'A seasoned warrior with a mysterious past. He carries an ancient sword that glows with blue fire.',
        appearances: 12,
        relationships: ['Aria Moonwhisper', 'Captain Blackheart'],
        createdAt: new Date().toISOString(),
        project: { name: 'The Chronicles of Aetheria' },
      },
      {
        id: '3',
        name: 'Emma Chen',
        description: 'A talented architect who moves to a small coastal town to start fresh after a difficult breakup.',
        appearances: 8,
        relationships: ['Jake Morrison', 'Mrs. Patterson'],
        createdAt: new Date().toISOString(),
        project: { name: 'Modern Romance' },
      },
    ];

    setCharacters(mockCharacters);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const relationshipsArray = formData.relationships
      .split(',')
      .map(rel => rel.trim())
      .filter(rel => rel.length > 0);

    const characterData = {
      ...formData,
      relationships: relationshipsArray,
      appearances: 0,
      createdAt: new Date().toISOString(),
      project: { name: 'Current Project' },
    };

    if (editingCharacter) {
      setCharacters(prev => 
        prev.map(char => 
          char.id === editingCharacter.id 
            ? { ...char, ...characterData }
            : char
        )
      );
      setEditingCharacter(null);
    } else {
      setCharacters(prev => [...prev, { ...characterData, id: Date.now().toString() }]);
    }

    setFormData({ name: '', description: '', relationships: '' });
    setIsAddingCharacter(false);
  };

  const handleEdit = (character) => {
    setEditingCharacter(character);
    setFormData({
      name: character.name,
      description: character.description || '',
      relationships: character.relationships?.join(', ') || '',
    });
    setIsAddingCharacter(true);
  };

  const handleDelete = (id) => {
    setCharacters(prev => prev.filter(char => char.id !== id));
  };

  const handleCancel = () => {
    setIsAddingCharacter(false);
    setEditingCharacter(null);
    setFormData({ name: '', description: '', relationships: '' });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-medium text-gray-800 mb-2">
                Character Dashboard
              </h1>
              <p className="text-lg text-gray-600">
                Manage your story characters
              </p>
            </div>
            <Button onClick={() => setIsAddingCharacter(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Character
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Characters</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{characters.length}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {new Set(characters.map(c => c.project?.name)).size}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Appearances</CardTitle>
              <User className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {characters.reduce((acc, char) => acc + char.appearances, 0)}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Add/Edit Character Form */}
        {isAddingCharacter && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>
                {editingCharacter ? 'Edit Character' : 'Add New Character'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Name</label>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Character name"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Description</label>
                  <Textarea
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Character description, personality, background..."
                    rows={4}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Relationships (comma-separated)
                  </label>
                  <Input
                    value={formData.relationships}
                    onChange={(e) => setFormData(prev => ({ ...prev, relationships: e.target.value }))}
                    placeholder="Other characters this character is related to"
                  />
                </div>

                <div className="flex space-x-2">
                  <Button type="submit">
                    {editingCharacter ? 'Update Character' : 'Add Character'}
                  </Button>
                  <Button type="button" variant="outline" onClick={handleCancel}>
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Characters Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {characters.map((character) => (
            <CharacterCard
              key={character.id}
              character={character}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}

          {characters.length === 0 && !isAddingCharacter && (
            <Card className="col-span-full text-center py-12">
              <CardContent>
                <User className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <h3 className="text-lg font-medium text-gray-500 mb-2">
                  No characters yet
                </h3>
                <p className="text-gray-400 mb-4">
                  Start by adding your first character to begin building your story world.
                </p>
                <Button onClick={() => setIsAddingCharacter(true)}>
                  Add Your First Character
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default CharacterProfile;

