import React, { useState } from 'react';

interface KnowledgeNode {
  id: string;
  title: string;
  type: string;
  content?: string;
  children?: KnowledgeNode[];
  isExpanded?: boolean;
  metadata?: {
    score?: number;
  };
}

export const KnowledgeExplorer: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  // Mock knowledge nodes
  const knowledgeNodes: KnowledgeNode[] = [
    {
      id: '1',
      title: 'Chonost Development Roadmap',
      type: 'document',
      content: 'Phase 2: Advanced AI & Background Services',
      children: [],
      isExpanded: false,
      metadata: { score: 0.95 }
    },
    {
      id: '2',
      title: 'The Trinity Layout Design',
      type: 'document',
      content: 'Three main areas: Left Sidebar, Center Editor, Right Panel',
      children: [],
      isExpanded: false,
      metadata: { score: 0.87 }
    }
  ];

  const handleNodeClick = (node: KnowledgeNode) => {
    setSelectedNode(node.id);
    console.log('Selected node:', node.title);
  };

  const toggleNodeExpansion = (nodeId: string) => {
    console.log(`Toggle node: ${nodeId}`);
  };

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'document': return '📄';
      case 'folder': return '📁';
      case 'note': return '📝';
      default: return '📋';
    }
  };

  const filteredNodes = searchQuery.trim()
    ? knowledgeNodes.filter(node =>
        node.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.content?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : knowledgeNodes;

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
        ) : (
          <div className="knowledge-nodes">
            {filteredNodes.map((node) => (
              <div key={node.id} className="node-container mb-2">
                {/* Parent Node */}
                <div
                  className={`parent-node flex items-center space-x-2 px-2 py-1 rounded cursor-pointer hover:bg-gray-100 ${
                    selectedNode === node.id ? 'bg-blue-100 text-blue-700' : ''
                  }`}
                  onClick={() => handleNodeClick(node)}
                >
                  <span className="node-icon">{getNodeIcon(node.type)}</span>
                  <span className="node-title text-sm font-medium">{node.title}</span>
                  {node.metadata?.score && (
                    <span className="text-xs text-gray-400 ml-auto">
                      {(node.metadata.score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>

                {node.content && (
                  <div className="node-content text-xs text-gray-500 mt-1 px-2">
                    {node.content.substring(0, 60)}...
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="explorer-footer bg-gray-50 border-t border-gray-200 px-4 py-2">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            {searchQuery.trim()
              ? `Search results: ${filteredNodes.length}`
              : `Total nodes: ${knowledgeNodes.length}`
            }
          </span>
          <button
            className="text-blue-600 hover:text-blue-800"
            onClick={() => {
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
