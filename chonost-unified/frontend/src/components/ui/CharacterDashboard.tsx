import React, { useState } from 'react';
import { Card } from './Card';
import { Button } from './Button';
import { Input } from './Input';
import { Typography } from './Typography';
import { Icon } from './Icon';

interface Character {
  id: string;
  name: string;
  description?: string;
  appearances: number;
  relationships: string[];
  createdAt: string;
  project?: { name: string };
}

interface CharacterCardProps {
  character: Character;
  onEdit: (character: Character) => void;
  onDelete: (id: string) => void;
}

const CharacterCard: React.FC<CharacterCardProps> = ({ character, onEdit, onDelete }) => {
  return (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
            <Icon name="user" size="md" color="#2563eb" />
          </div>
          <div>
            <Typography variant="h4" className="mb-0">{character.name}</Typography>
            <Typography variant="caption" className="mb-0">
              {character.appearances} appearances
            </Typography>
          </div>
        </div>
        <div className="flex space-x-2">
          <Button variant="secondary" size="sm" onClick={() => onEdit(character)}>
            Edit
          </Button>
          <Button variant="outline" size="sm" onClick={() => onDelete(character.id)}>
            Delete
          </Button>
        </div>
      </div>

      {character.description && (
        <Typography variant="body" className="text-gray-600 mb-4 line-clamp-3">
          {character.description}
        </Typography>
      )}

      {character.relationships && character.relationships.length > 0 && (
        <div className="mb-4">
          <Typography variant="caption" className="font-medium text-gray-700 mb-2">
            Relationships:
          </Typography>
          <div className="flex flex-wrap gap-1">
            {character.relationships.slice(0, 3).map((rel, index) => (
              <span key={index} className="px-2 py-1 bg-gray-100 text-xs rounded-md">
                {rel}
              </span>
            ))}
            {character.relationships.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-xs rounded-md">
                +{character.relationships.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>Created {new Date(character.createdAt).toLocaleDateString()}</span>
        <span className="px-2 py-1 bg-blue-50 text-blue-600 rounded-md text-xs">
          {character.project?.name}
        </span>
      </div>
    </Card>
  );
};

export const CharacterDashboard: React.FC = () => {
  const [characters, setCharacters] = useState<Character[]>([
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
  ]);

  const [isAddingCharacter, setIsAddingCharacter] = useState(false);
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    relationships: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
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

  const handleEdit = (character: Character) => {
    setEditingCharacter(character);
    setFormData({
      name: character.name,
      description: character.description || '',
      relationships: character.relationships?.join(', ') || '',
    });
    setIsAddingCharacter(true);
  };

  const handleDelete = (id: string) => {
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
              <Typography variant="h1" className="mb-2">
                Character Dashboard
              </Typography>
              <Typography variant="body" className="text-gray-600">
                Manage your story characters
              </Typography>
            </div>
            <Button onClick={() => setIsAddingCharacter(true)}>
              Add Character
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card title="Total Characters">
            <Typography variant="h2" className="mb-0">{characters.length}</Typography>
          </Card>

          <Card title="Active Projects">
            <Typography variant="h2" className="mb-0">
              {new Set(characters.map(c => c.project?.name)).size}
            </Typography>
          </Card>

          <Card title="Total Appearances">
            <Typography variant="h2" className="mb-0">
              {characters.reduce((acc, char) => acc + char.appearances, 0)}
            </Typography>
          </Card>
        </div>

        {/* Add/Edit Character Form */}
        {isAddingCharacter && (
          <Card title={editingCharacter ? 'Edit Character' : 'Add New Character'} className="mb-8">
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Name"
                value={formData.name}
                onChange={(value) => setFormData(prev => ({ ...prev, name: value }))}
                placeholder="Character name"
              />

              <Input
                type="textarea"
                label="Description"
                value={formData.description}
                onChange={(value) => setFormData(prev => ({ ...prev, description: value }))}
                placeholder="Character description, personality, background..."
                rows={4}
              />

              <Input
                label="Relationships (comma-separated)"
                value={formData.relationships}
                onChange={(value) => setFormData(prev => ({ ...prev, relationships: value }))}
                placeholder="Other characters this character is related to"
              />

              <div className="flex space-x-2">
                <Button type="submit">
                  {editingCharacter ? 'Update Character' : 'Add Character'}
                </Button>
                <Button variant="outline" onClick={handleCancel}>
                  Cancel
                </Button>
              </div>
            </form>
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
              <div className="flex flex-col items-center">
                <Icon name="user" size="lg" className="mb-4 text-gray-400" />
                <Typography variant="h3" className="text-gray-500 mb-2">
                  No characters yet
                </Typography>
                <Typography variant="body" className="text-gray-400 mb-4">
                  Start by adding your first character to begin building your story world.
                </Typography>
                <Button onClick={() => setIsAddingCharacter(true)}>
                  Add Your First Character
                </Button>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

