import React, { useEffect, useRef } from 'react';
import { Card } from './Card';
import { Typography } from './Typography';

interface Character {
  id: string;
  name: string;
  relationships: string[];
  appearances: number;
}

interface CharacterRelationshipMapProps {
  characters: Character[];
  className?: string;
}

export const CharacterRelationshipMap: React.FC<CharacterRelationshipMapProps> = ({
  characters,
  className = '',
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || characters.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = 600;
    canvas.height = 400;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Calculate positions for characters in a circle
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) * 0.3;

    const characterPositions = characters.map((character, index) => {
      const angle = (index / characters.length) * 2 * Math.PI;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;
      return { character, x, y };
    });

    // Draw relationships (lines between characters)
    ctx.strokeStyle = '#E5E7EB';
    ctx.lineWidth = 1;
    
    characterPositions.forEach(({ character, x, y }) => {
      character.relationships.forEach(relationshipName => {
        const relatedCharacter = characterPositions.find(
          pos => pos.character.name === relationshipName
        );
        
        if (relatedCharacter) {
          ctx.beginPath();
          ctx.moveTo(x, y);
          ctx.lineTo(relatedCharacter.x, relatedCharacter.y);
          ctx.stroke();
        }
      });
    });

    // Draw character nodes
    characterPositions.forEach(({ character, x, y }) => {
      // Calculate node size based on appearances
      const nodeSize = Math.max(20, Math.min(40, character.appearances * 2));
      
      // Draw node circle
      ctx.fillStyle = '#3B82F6';
      ctx.beginPath();
      ctx.arc(x, y, nodeSize, 0, 2 * Math.PI);
      ctx.fill();

      // Draw character name
      ctx.fillStyle = '#1F2937';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(character.name, x, y + nodeSize + 15);
      
      // Draw appearance count
      ctx.fillStyle = '#6B7280';
      ctx.font = '10px sans-serif';
      ctx.fillText(`${character.appearances}`, x, y + nodeSize + 28);
    });

  }, [characters]);

  if (characters.length === 0) {
    return (
      <Card title="Character Relationship Map" className={className}>
        <div className="flex flex-col items-center justify-center h-64 text-gray-500">
          <Typography variant="body" className="text-center">
            No characters to display. Add some characters to see their relationships.
          </Typography>
        </div>
      </Card>
    );
  }

  return (
    <Card title="Character Relationship Map" className={className}>
      <div className="space-y-4">
        <Typography variant="body" className="text-gray-600">
          Visual representation of character relationships and their importance in the story.
          Node size represents the number of appearances.
        </Typography>
        
        <div className="flex justify-center">
          <canvas
            ref={canvasRef}
            className="border border-gray-200 rounded-lg"
            style={{ maxWidth: '100%', height: 'auto' }}
          />
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
          {characters.map((character) => (
            <div key={character.id} className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-blue-600 rounded-full"></div>
              <div>
                <Typography variant="caption" className="font-medium mb-0">
                  {character.name}
                </Typography>
                <Typography variant="caption" className="text-gray-500 mb-0">
                  {character.appearances} appearances
                </Typography>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};

