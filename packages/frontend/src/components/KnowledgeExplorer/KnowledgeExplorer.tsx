import React, { useState, useEffect } from 'react';
import { useAppStore } from '../../store/appStore';
import { knowledgeService, KnowledgeNode } from '../../services/knowledgeService';

interface KnowledgeExplorerProps {
  // Add props here
}

export const KnowledgeExplorer: React.FC<KnowledgeExplorerProps> = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [knowledgeNodes, setKnowledgeNodes] = useState<KnowledgeNode[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchResults, setSearchResults] = useState<KnowledgeNode[]>([]);
  const { documents, setCurrentDocument } = useAppStore();

  // Load knowledge graph on component mount
  useEffect(() => {
    loadKnowledgeGraph();
  }, []);

  // Search knowledge when query changes
  useEffect(() => {
    if (searchQuery.trim()) {
      searchKnowledge();
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const loadKnowledgeGraph = async () => {
    try {
      setIsLoading(true);
      const graph = await knowledgeService.getKnowledgeGraph();
      setKnowledgeNodes(graph);
    } catch (error) {
      console.error('Error loading knowledge graph:', error);
      // Fallback to mock data
      setKnowledgeNodes([
        {
          id: '1',
          title: 'Documents',
          type: 'document',
          isExpanded: true,
          children: documents.map(doc => ({
            id: doc.id,
            title: doc.title,
            type: 'document' as const,
          })),
        },
        {
          id: '2',
          title: 'Characters',
          type: 'character',
          isExpanded: false,
          children: [
            { id: 'char1', title: 'John Smith', type: 'character' },
            { id: 'char2', title: 'Mary Johnson', type: 'character' },
          ],
        },
        {
          id: '3',
          title: 'Locations',
          type: 'location',
          isExpanded: false,
          children: [
            { id: 'loc1', title: 'New York', type: 'location' },
            { id: 'loc2', title: 'London', type: 'location' },
          ],
        },
        {
          id: '4',
          title: 'Concepts',
          type: 'concept',
          isExpanded: false,
          children: [
            { id: 'concept1', title: 'Love', type: 'concept' },
            { id: 'concept2', title: 'Betrayal', type: 'concept' },
          ],
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const searchKnowledge = async () => {
    try {
      const results = await knowledgeService.searchKnowledge(searchQuery, 5);
      const searchNodes = results.map(result => ({
        id: result.id,
        title: result.title,
        type: 'document' as const,
        content: result.content,
        metadata: { score: result.score }
      }));
      setSearchResults(searchNodes);
    } catch (error) {
      console.error('Error searching knowledge:', error);
      setSearchResults([]);
    }
  };

  const handleNodeClick = (node: KnowledgeNode) => {
    setSelectedNode(node.id);
    
    // If it's a document, load it
    if (node.type === 'document') {
      const document = documents.find(doc => doc.id === node.id);
      if (document) {
        setCurrentDocument(document);
      }
    }
  };

  const toggleNodeExpansion = (nodeId: string) => {
    // Implementation for expanding/collapsing nodes
    console.log(`Toggle node: ${nodeId}`);
  };

  const getNodeIcon = (type: KnowledgeNode['type']) => {
    switch (type) {
      case 'document':
        return '📄';
      case 'character':
        return '👤';
      case 'location':
        return '📍';
      case 'concept':
        return '💡';
      case 'note':
        return '📝';
      default:
        return '📁';
    }
  };

  const filteredNodes = knowledgeNodes.filter(node =>
    node.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    node.children?.some(child => 
      child.title.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  return (
    <div className="knowledge-explorer-container w-80 bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="explorer-header bg-gray-50 border-b border-gray-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Knowledge Explorer</h2>
        
        {/* Search */}
        <div className="search-container relative">
          <input
            type="text"
            placeholder="Search knowledge..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <span className="absolute right-3 top-2.5 text-gray-400">🔍</span>
        </div>
      </div>

      {/* Knowledge Tree */}
      <div className="knowledge-tree flex-1 overflow-y-auto p-2">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <span className="ml-2 text-sm text-gray-500">Loading...</span>
          </div>
        ) : searchQuery.trim() && searchResults.length > 0 ? (
          // Show search results
          <div className="search-results">
            <div className="text-xs text-gray-500 mb-2 px-2">
              Search results for "{searchQuery}" ({searchResults.length})
            </div>
            {searchResults.map((node) => (
              <div
                key={node.id}
                className={`search-result flex items-center space-x-2 px-2 py-1 rounded cursor-pointer hover:bg-blue-50 ${
                  selectedNode === node.id ? 'bg-blue-100 text-blue-700' : ''
                }`}
                onClick={() => handleNodeClick(node)}
              >
                <span className="node-icon text-sm">🔍</span>
                <div className="flex-1 min-w-0">
                  <div className="node-title text-sm font-medium truncate">{node.title}</div>
                  {node.content && (
                    <div className="node-content text-xs text-gray-500 truncate">
                      {node.content.substring(0, 60)}...
                    </div>
                  )}
                </div>
                {node.metadata?.score && (
                  <span className="text-xs text-gray-400">
                    {(node.metadata.score * 100).toFixed(0)}%
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          // Show regular knowledge tree
          filteredNodes.map((node) => (
          <div key={node.id} className="node-container">
            {/* Parent Node */}
            <div
              className={`parent-node flex items-center space-x-2 px-2 py-1 rounded cursor-pointer hover:bg-gray-100 ${
                selectedNode === node.id ? 'bg-blue-100 text-blue-700' : ''
              }`}
              onClick={() => handleNodeClick(node)}
            >
              <button
                className="expand-btn w-4 h-4 flex items-center justify-center text-xs"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleNodeExpansion(node.id);
                }}
              >
                {node.children && node.children.length > 0 ? (
                  node.isExpanded ? '▼' : '▶'
                ) : (
                  <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                )}
              </button>
              
              <span className="node-icon">{getNodeIcon(node.type)}</span>
              <span className="node-title text-sm font-medium">{node.title}</span>
              
              {node.children && (
                <span className="node-count text-xs text-gray-500 ml-auto">
                  {node.children.length}
                </span>
              )}
            </div>

            {/* Child Nodes */}
            {node.isExpanded && node.children && (
              <div className="child-nodes ml-6">
                {node.children.map((child) => (
                  <div
                    key={child.id}
                    className={`child-node flex items-center space-x-2 px-2 py-1 rounded cursor-pointer hover:bg-gray-100 ${
                      selectedNode === child.id ? 'bg-blue-100 text-blue-700' : ''
                    }`}
                    onClick={() => handleNodeClick(child)}
                  >
                    <span className="node-icon text-sm">{getNodeIcon(child.type)}</span>
                    <span className="node-title text-sm">{child.title}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="explorer-footer bg-gray-50 border-t border-gray-200 px-4 py-2">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            {searchQuery.trim() 
              ? `Search results: ${searchResults.length}`
              : `Total nodes: ${knowledgeNodes.length}`
            }
          </span>
          <button 
            className="text-blue-600 hover:text-blue-800"
            onClick={() => {
              // TODO: Implement add document functionality
              console.log('Add document clicked');
            }}
          >
            + Add Document
          </button>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeExplorer;
