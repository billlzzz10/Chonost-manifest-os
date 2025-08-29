import React from 'react';
import { Card } from '../molecules/Card';
import { Typography } from '../atoms/Typography';
import { Button } from '../atoms/Button';
import { Icon } from '../atoms/Icon';

interface Character {
  id: string;
  name: string;
  description?: string;
  relationships?: string[];
  appearances?: number;
}

interface CharacterDashboardProps {
  characters: Character[];
  onCharacterSelect?: (character: Character) => void;
  onAddCharacter?: () => void;
  className?: string;
}

export const CharacterDashboard: React.FC<CharacterDashboardProps> = ({
  characters,
  onCharacterSelect,
  onAddCharacter,
  className = '',
}) => {
  return (
    <div className={`space-y-6 ${className}`}>
      <div className="flex justify-between items-center">
        <Typography variant="h2">Character Dashboard</Typography>
        {onAddCharacter && (
          <Button onClick={onAddCharacter} variant="primary">
            <div className="flex items-center space-x-2">
              <Icon name="user" size="sm" />
              <span>Add Character</span>
            </div>
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {characters.map((character) => (
          <Card
            key={character.id}
            className="hover:shadow-xl transition-shadow duration-200 cursor-pointer"
            onClick={() => onCharacterSelect && onCharacterSelect(character)}
          >
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Icon name="user" size="md" color="#3B82F6" />
                </div>
                <div>
                  <Typography variant="h4" className="mb-0">
                    {character.name}
                  </Typography>
                  {character.appearances && (
                    <Typography variant="caption" className="mb-0">
                      {character.appearances} appearances
                    </Typography>
                  )}
                </div>
              </div>

              {character.description && (
                <Typography variant="body" className="text-gray-600 line-clamp-3">
                  {character.description}
                </Typography>
              )}

              {character.relationships && character.relationships.length > 0 && (
                <div>
                  <Typography variant="caption" className="font-medium mb-2">
                    Relationships:
                  </Typography>
                  <div className="flex flex-wrap gap-1">
                    {character.relationships.slice(0, 3).map((rel, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-xs rounded-full text-gray-600"
                      >
                        {rel}
                      </span>
                    ))}
                    {character.relationships.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-xs rounded-full text-gray-600">
                        +{character.relationships.length - 3} more
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>

      {characters.length === 0 && (
        <Card className="text-center py-12">
          <Icon name="user" size="lg" className="mx-auto mb-4 text-gray-400" />
          <Typography variant="h3" className="text-gray-500 mb-2">
            No characters yet
          </Typography>
          <Typography variant="body" className="text-gray-400 mb-4">
            Start by adding your first character to begin building your story world.
          </Typography>
          {onAddCharacter && (
            <Button onClick={onAddCharacter} variant="primary">
              Add Your First Character
            </Button>
          )}
        </Card>
      )}
    </div>
  );
};

