import React, { useState } from 'react';
import { Card } from './Card';
import { Button } from './Button';
import { Input } from './Input';
import { Typography } from './Typography';
import { Icon } from './Icon';

interface AnalyzedCharacter {
  name: string;
  mentions: number;
  contexts: string[];
  relationships: string[];
}

interface MarkdownAnalyzerProps {
  onCharactersAnalyzed?: (characters: AnalyzedCharacter[]) => void;
  className?: string;
}

export const MarkdownAnalyzer: React.FC<MarkdownAnalyzerProps> = ({
  onCharactersAnalyzed,
  className = '',
}) => {
  const [content, setContent] = useState('');
  const [analyzedCharacters, setAnalyzedCharacters] = useState<AnalyzedCharacter[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const analyzeCharacters = () => {
    setIsAnalyzing(true);
    
    // Simple character analysis algorithm
    setTimeout(() => {
      const characters = extractCharacters(content);
      setAnalyzedCharacters(characters);
      if (onCharactersAnalyzed) {
        onCharactersAnalyzed(characters);
      }
      setIsAnalyzing(false);
    }, 1000);
  };

  const extractCharacters = (text: string): AnalyzedCharacter[] => {
    // Extract potential character names (capitalized words)
    const namePattern = /\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g;
    const matches = text.match(namePattern) || [];
    
    // Filter out common words
    const commonWords = ['The', 'This', 'That', 'Chapter', 'Section', 'Part', 'When', 'Where', 'What', 'Who', 'How', 'Why'];
    const potentialNames = matches.filter(name => 
      !commonWords.includes(name) && 
      name.length > 2 &&
      !name.match(/^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$/) &&
      !name.match(/^(January|February|March|April|May|June|July|August|September|October|November|December)$/)
    );

    // Count mentions and extract contexts
    const characterMap = new Map<string, AnalyzedCharacter>();
    
    potentialNames.forEach(name => {
      if (!characterMap.has(name)) {
        characterMap.set(name, {
          name,
          mentions: 0,
          contexts: [],
          relationships: [],
        });
      }
      
      const character = characterMap.get(name)!;
      character.mentions++;
      
      // Extract context (sentence containing the character)
      const sentences = text.split(/[.!?]+/);
      const contextSentences = sentences.filter(sentence => 
        sentence.toLowerCase().includes(name.toLowerCase())
      ).slice(0, 3); // Limit to 3 contexts
      
      character.contexts = [...new Set([...character.contexts, ...contextSentences])];
    });

    // Find relationships (characters mentioned in the same sentences)
    characterMap.forEach((character, name) => {
      const relationships = new Set<string>();
      
      character.contexts.forEach(context => {
        characterMap.forEach((otherChar, otherName) => {
          if (name !== otherName && context.toLowerCase().includes(otherName.toLowerCase())) {
            relationships.add(otherName);
          }
        });
      });
      
      character.relationships = Array.from(relationships);
    });

    // Filter characters with at least 2 mentions
    return Array.from(characterMap.values())
      .filter(char => char.mentions >= 2)
      .sort((a, b) => b.mentions - a.mentions);
  };

  return (
    <div className={`space-y-6 ${className}`}>
      <Card title="Markdown Character Analyzer">
        <Typography variant="body" className="mb-4">
          Paste your markdown content below to automatically analyze and extract characters from your story.
        </Typography>
        
        <Input
          type="textarea"
          value={content}
          onChange={setContent}
          placeholder="Paste your markdown content here..."
          rows={10}
          className="mb-4"
        />
        
        <Button 
          onClick={analyzeCharacters}
          disabled={!content.trim() || isAnalyzing}
          className="w-full"
        >
          {isAnalyzing ? 'Analyzing...' : 'Analyze Characters'}
        </Button>
      </Card>

      {analyzedCharacters.length > 0 && (
        <Card title="Analyzed Characters">
          <div className="space-y-4">
            {analyzedCharacters.map((character, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <Typography variant="h4" className="mb-0">{character.name}</Typography>
                  <div className="flex items-center space-x-2">
                    <Icon name="user" size="sm" />
                    <Typography variant="caption" className="mb-0">
                      {character.mentions} mentions
                    </Typography>
                  </div>
                </div>
                
                {character.relationships.length > 0 && (
                  <div className="mb-3">
                    <Typography variant="caption" className="font-medium mb-2">
                      Relationships:
                    </Typography>
                    <div className="flex flex-wrap gap-1">
                      {character.relationships.map((rel, relIndex) => (
                        <span 
                          key={relIndex}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-md"
                        >
                          {rel}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {character.contexts.length > 0 && (
                  <div>
                    <Typography variant="caption" className="font-medium mb-2">
                      Sample contexts:
                    </Typography>
                    <div className="space-y-1">
                      {character.contexts.slice(0, 2).map((context, contextIndex) => (
                        <Typography 
                          key={contextIndex}
                          variant="caption" 
                          className="text-gray-600 italic block"
                        >
                          "{context.trim()}..."
                        </Typography>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

