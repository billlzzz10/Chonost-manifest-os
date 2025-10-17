import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@ui/card';
import { Button } from '@ui/button';
import { Input } from '@ui/input';
import { Textarea } from '@ui/textarea';
import { Label } from '@ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@ui/select';
import { Badge } from '@ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@ui/tabs';
import { ScrollArea } from '@ui/scroll-area';
import { Separator } from '@ui/separator';
import { 
  Plus, 
  Save, 
  Play, 
  Settings, 
  Code, 
  Brain, 
  Zap,
  Trash2,
  Edit,
  Copy,
  Star,
  Download
} from 'lucide-react';
import { useToast } from '@ui/hooks/use-toast';

const AgentBuilder = () => {
  const [agents, setAgents] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [currentAgent, setCurrentAgent] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const [agentForm, setAgentForm] = useState({
    name: '',
    description: '',
    config: {
      capabilities: [],
      tools: [],
      prompt_template: '',
      parameters: {}
    }
  });

  const availableCapabilities = [
    { id: 'text_generation', name: 'Text Generation', description: 'Generate human-like text' },
    { id: 'data_analysis', name: 'Data Analysis', description: 'Analyze and process data' },
    { id: 'code_generation', name: 'Code Generation', description: 'Generate and review code' },
    { id: 'web_search', name: 'Web Search', description: 'Search the web for information' },
    { id: 'image_processing', name: 'Image Processing', description: 'Process and analyze images' },
    { id: 'api_integration', name: 'API Integration', description: 'Integrate with external APIs' },
    { id: 'workflow_automation', name: 'Workflow Automation', description: 'Automate complex workflows' },
    { id: 'summarization', name: 'Summarization', description: 'Summarize long content' }
  ];

  const availableTools = [
    { id: 'openai', name: 'OpenAI API', description: 'Access to GPT models' },
    { id: 'requests', name: 'HTTP Requests', description: 'Make HTTP requests' },
    { id: 'pandas', name: 'Pandas', description: 'Data manipulation library' },
    { id: 'matplotlib', name: 'Matplotlib', description: 'Data visualization' },
    { id: 'beautifulsoup', name: 'BeautifulSoup', description: 'Web scraping' },
    { id: 'selenium', name: 'Selenium', description: 'Browser automation' },
    { id: 'pillow', name: 'Pillow', description: 'Image processing' },
    { id: 'nltk', name: 'NLTK', description: 'Natural language processing' }
  ];

  useEffect(() => {
    // TODO: Re-enable API calls when backend is ready
    // fetchAgents();
    // fetchTemplates();
  }, []);

  const fetchAgents = async () => {
    // TODO: Implement API call to fetch agents
    console.log("Fetching agents...");
    setLoading(false);
  };

  const fetchTemplates = async () => {
    // TODO: Implement API call to fetch templates
    console.log("Fetching templates...");
  };

  const handleCreateAgent = () => {
    setCurrentAgent(null);
    setAgentForm({
      name: '',
      description: '',
      config: {
        capabilities: [],
        tools: [],
        prompt_template: '',
        parameters: {}
      }
    });
    setIsEditing(true);
  };

  const handleEditAgent = (agent) => {
    setCurrentAgent(agent);
    setAgentForm({
      name: agent.name,
      description: agent.description,
      config: agent.config
    });
    setIsEditing(true);
  };

  const handleSaveAgent = async () => {
    // TODO: Implement API call to save the agent
    setLoading(true);
    console.log("Saving agent:", agentForm);
    setTimeout(() => {
      toast({
        title: "Success (Mock)",
        description: `Agent ${currentAgent ? 'updated' : 'created'} successfully`
      });
      setIsEditing(false);
      setLoading(false);
      // fetchAgents(); // This would refetch the list
    }, 1000);
  };

  const handleDeleteAgent = async (agentId) => {
    if (!confirm('Are you sure you want to delete this agent?')) return;
    // TODO: Implement API call to delete the agent
    setLoading(true);
    console.log("Deleting agent:", agentId);
    setTimeout(() => {
      toast({
        title: "Success (Mock)",
        description: "Agent deleted successfully"
      });
      setLoading(false);
      // fetchAgents(); // This would refetch the list
    }, 1000);
  };

  const handleExecuteAgent = async (agent) => {
    // TODO: Implement API call to execute the agent
    const inputData = prompt('Enter input data for the agent (JSON format):');
    if (!inputData) return;
    setLoading(true);
    console.log("Executing agent:", agent.id, "with data:", inputData);
    setTimeout(() => {
      toast({
        title: "Execution Started (Mock)",
        description: `Agent execution completed with status: success`
      });
      setLoading(false);
    }, 1500);
  };

  const handleUseTemplate = (template) => {
    setCurrentAgent(null);
    setAgentForm({
      name: `${template.name} (Copy)`,
      description: template.description,
      config: template.template_config
    });
    setIsEditing(true);
  };

  const toggleCapability = (capabilityId) => {
    setAgentForm(prev => ({
      ...prev,
      config: {
        ...prev.config,
        capabilities: prev.config.capabilities.includes(capabilityId)
          ? prev.config.capabilities.filter(id => id !== capabilityId)
          : [...prev.config.capabilities, capabilityId]
      }
    }));
  };

  const toggleTool = (toolId) => {
    setAgentForm(prev => ({
      ...prev,
      config: {
        ...prev.config,
        tools: prev.config.tools.includes(toolId)
          ? prev.config.tools.filter(id => id !== toolId)
          : [...prev.config.tools, toolId]
      }
    }));
  };

  if (isEditing) {
    return (
      <div className="container mx-auto p-6 max-w-4xl">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">
            {currentAgent ? 'Edit Agent' : 'Create New Agent'}
          </h1>
          <div className="space-x-2">
            <Button variant="outline" onClick={() => setIsEditing(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveAgent} disabled={loading}>
              <Save className="w-4 h-4 mr-2" />
              Save Agent
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="name">Agent Name</Label>
                  <Input
                    id="name"
                    value={agentForm.name}
                    onChange={(e) => setAgentForm(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Enter agent name"
                  />
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={agentForm.description}
                    onChange={(e) => setAgentForm(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Describe what this agent does"
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Capabilities</CardTitle>
                <CardDescription>Select the capabilities your agent should have</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {availableCapabilities.map((capability) => (
                    <div
                      key={capability.id}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        agentForm.config.capabilities.includes(capability.id)
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => toggleCapability(capability.id)}
                    >
                      <div className="font-medium">{capability.name}</div>
                      <div className="text-sm text-gray-500">{capability.description}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tools & Integrations</CardTitle>
                <CardDescription>Select the tools your agent can use</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {availableTools.map((tool) => (
                    <div
                      key={tool.id}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        agentForm.config.tools.includes(tool.id)
                          ? 'border-green-500 bg-green-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => toggleTool(tool.id)}
                    >
                      <div className="font-medium">{tool.name}</div>
                      <div className="text-sm text-gray-500">{tool.description}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Prompt Template</CardTitle>
                <CardDescription>Define how your agent should process inputs</CardDescription>
              </CardHeader>
              <CardContent>
                <Textarea
                  value={agentForm.config.prompt_template}
                  onChange={(e) => setAgentForm(prev => ({
                    ...prev,
                    config: { ...prev.config, prompt_template: e.target.value }
                  }))}
                  placeholder="Enter your prompt template here. Use {input} for user input and other variables as needed."
                  rows={6}
                  className="font-mono"
                />
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Preview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Selected Capabilities</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {agentForm.config.capabilities.map((capId) => {
                      const cap = availableCapabilities.find(c => c.id === capId);
                      return cap ? (
                        <Badge key={capId} variant="secondary">
                          {cap.name}
                        </Badge>
                      ) : null;
                    })}
                  </div>
                </div>
                <div>
                  <Label>Selected Tools</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {agentForm.config.tools.map((toolId) => {
                      const tool = availableTools.find(t => t.id === toolId);
                      return tool ? (
                        <Badge key={toolId} variant="outline">
                          {tool.name}
                        </Badge>
                      ) : null;
                    })}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Custom Agent Builder</h1>
        <Button onClick={handleCreateAgent}>
          <Plus className="w-4 h-4 mr-2" />
          Create New Agent
        </Button>
      </div>

      <Tabs defaultValue="agents" className="space-y-6">
        <TabsList>
          <TabsTrigger value="agents">My Agents</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
        </TabsList>

        <TabsContent value="agents" className="space-y-6">
          {loading ? (
            <div className="text-center py-8">Loading agents...</div>
          ) : agents.length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <Brain className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium mb-2">No agents yet</h3>
                <p className="text-gray-500 mb-4">Create your first custom agent to get started</p>
                <Button onClick={handleCreateAgent}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Agent
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {agents.map((agent) => (
                <Card key={agent.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-lg">{agent.name}</CardTitle>
                        <CardDescription className="mt-1">
                          {agent.description}
                        </CardDescription>
                      </div>
                      <Badge variant={agent.is_active ? "default" : "secondary"}>
                        {agent.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <Label className="text-sm font-medium">Capabilities</Label>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {agent.config.capabilities?.slice(0, 3).map((cap) => (
                            <Badge key={cap} variant="secondary" className="text-xs">
                              {cap.replace('_', ' ')}
                            </Badge>
                          ))}
                          {agent.config.capabilities?.length > 3 && (
                            <Badge variant="secondary" className="text-xs">
                              +{agent.config.capabilities.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleExecuteAgent(agent)}
                          className="flex-1"
                        >
                          <Play className="w-3 h-3 mr-1" />
                          Run
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEditAgent(agent)}
                        >
                          <Edit className="w-3 h-3" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteAgent(agent.id)}
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="templates" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map((template) => (
              <Card key={template.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                      <CardDescription className="mt-1">
                        {template.description}
                      </CardDescription>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Star className="w-4 h-4 text-yellow-400" />
                      <span className="text-sm">{template.rating || 0}</span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <Badge variant="outline">{template.category}</Badge>
                    </div>
                    <div className="text-sm text-gray-500">
                      Used {template.usage_count || 0} times
                    </div>
                    <Button
                      size="sm"
                      onClick={() => handleUseTemplate(template)}
                      className="w-full"
                    >
                      <Download className="w-3 h-3 mr-1" />
                      Use Template
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AgentBuilder;