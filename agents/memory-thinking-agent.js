const { useMCPTool, accessMCPResource } = require('../services/mcp-toolbox');

class MemoryThinkingAgent {
  constructor(config = {}) {
    this.memoryServer = 'memory';
    this.thinkingServer = 'sequentialthinking';
    this.config = {
      ...config,
      memoryFilePath: process.env.MEMORY_FILE_PATH || config.memoryFilePath || './memory.json'
    };
    this.context = new Map();
    this.thoughtHistory = [];
  }

  /**
   * เริ่มต้น memory graph สำหรับ code review context
   * @returns {Promise<void>}
   */
  async initializeMemoryGraph() {
    try {
      console.log('🧠 Initializing memory graph for code review...');
      
      // Create core entities for code review
      await this.createCoreEntities();
      
      // Create relationships between entities
      await this.createCoreRelations();
      
      console.log('✅ Memory graph initialized successfully');
    } catch (error) {
      console.error('❌ Error initializing memory graph:', error.message);
      throw error;
    }
  }

  /**
   * สร้าง core entities ใน knowledge graph
   * @returns {Promise<void>}
   */
  async createCoreEntities() {
    const entities = [
      {
        name: 'CodeReviewProcess',
        entityType: 'Process',
        observations: [
          'AI-powered code review workflow with automatic issue classification',
          'Handles critical and non-critical issues differently',
          'Integrates MCP tools for specialized analysis',
          'Supports fallback mechanisms for production readiness'
        ]
      },
      {
        name: 'CriticalIssues',
        entityType: 'IssueType',
        observations: [
          'Security vulnerabilities requiring manual review',
          'Breaking changes affecting API compatibility',
          'Major logic errors impacting functionality',
          'Data leaks and privacy concerns',
          'Requires detailed remediation paths and external audits'
        ]
      },
      {
        name: 'NonCriticalIssues',
        entityType: 'IssueType',
        observations: [
          'Formatting and style violations',
          'Documentation improvements',
          'Minor code style preferences',
          'Naming convention violations',
          'Can be automatically fixed and staged'
        ]
      },
      {
        name: 'CodacyIntegration',
        entityType: 'Tool',
        observations: [
          'Provides linting and security scanning capabilities',
          'Automated code quality analysis',
          'Security vulnerability detection',
          'Integration via MCP protocol'
        ]
      },
      {
        name: 'ProjectContext',
        entityType: 'Context',
        observations: [
          'Chonost Manuscript OS project structure',
          'Node.js based with multiple frontend applications',
          'AI-powered commit and version management system',
          'Uses OpenAI for natural language processing',
          'GitHub Actions for CI/CD workflows'
        ]
      }
    ];

    await useMCPTool({
      server_name: this.memoryServer,
      tool_name: 'create_entities',
      arguments: { entities }
    });
  }

  /**
   * สร้าง core relations ระหว่าง entities
   * @returns {Promise<void>}
   */
  async createCoreRelations() {
    const relations = [
      {
        from: 'CodeReviewProcess',
        to: 'CriticalIssues',
        relationType: 'handles'
      },
      {
        from: 'CodeReviewProcess',
        to: 'NonCriticalIssues',
        relationType: 'handles'
      },
      {
        from: 'CodeReviewProcess',
        to: 'CodacyIntegration',
        relationType: 'uses_tool'
      },
      {
        from: 'CodeReviewProcess',
        to: 'ProjectContext',
        relationType: 'operates_in'
      },
      {
        from: 'CriticalIssues',
        to: 'CodeReviewProcess',
        relationType: 'requires_manual_review'
      },
      {
        from: 'NonCriticalIssues',
        to: 'CodeReviewProcess',
        relationType: 'allows_auto_fix'
      }
    ];

    await useMCPTool({
      server_name: this.memoryServer,
      tool_name: 'create_relations',
      arguments: { relations }
    });
  }

  /**
   * เพิ่ม observations ใหม่ให้ entities
   * @param {string} entityName - ชื่อ entity
   * @param {Array<string>} observations - รายการ observations ใหม่
   * @returns {Promise<void>}
   */
  async addObservations(entityName, observations) {
    await useMCPTool({
      server_name: this.memoryServer,
      tool_name: 'add_observations',
      arguments: {
        observations: [{
          entityName,
          contents: observations
        }]
      }
    });
  }

  /**
   * Sequential thinking process สำหรับ code review decisions
   * @param {Object} reviewContext - Context ของการตรวจสอบ
   * @param {number} totalThoughts - จำนวน thoughts ที่ต้องการ (default: 5)
   * @returns {Promise<Object>} ผลลัพธ์การคิด
   */
  async performSequentialThinking(reviewContext, totalThoughts = 5) {
    console.log('🧠 Starting sequential thinking process...');
    
    let thoughtNumber = 1;
    let currentContext = { ...reviewContext };
    this.thoughtHistory = [];
    
    while (thoughtNumber <= totalThoughts) {
      console.log(`🤔 Thought ${thoughtNumber}/${totalThoughts}`);
      
      const thought = await this.generateThought(currentContext, thoughtNumber, totalThoughts);
      this.thoughtHistory.push(thought);
      
      // Update context based on thought
      currentContext = await this.updateContextFromThought(currentContext, thought);
      
      // Check if we need more thoughts
      if (!thought.nextThoughtNeeded) {
        console.log('✅ Sequential thinking completed');
        break;
      }
      
      thoughtNumber++;
    }
    
    // Generate final decision
    const finalDecision = await this.generateFinalDecision(currentContext);
    
    return {
      thoughts: this.thoughtHistory,
      finalDecision,
      context: currentContext,
      confidence: this.calculateConfidence()
    };
  }

  /**
   * สร้าง thought เดียวใน sequential thinking process
   * @param {Object} context - Context ปัจจุบัน
   * @param {number} thoughtNumber - ลำดับ thought
   * @param {number} totalThoughts - จำนวน thoughts ทั้งหมด
   * @returns {Promise<Object>}
   */
  async generateThought(context, thoughtNumber, totalThoughts) {
    const thoughtPrompt = `
Current context: ${JSON.stringify(context, null, 2)}

Thought ${thoughtNumber} of ${totalThoughts}:

1. Analyze the current situation
2. Identify key decision points
3. Consider previous thoughts and memory
4. Generate actionable insights
5. Determine if more analysis is needed

Requirements:
- Be specific and actionable
- Reference relevant entities from memory graph
- Consider both technical and business implications
- Evaluate risk vs. benefit
- Suggest next steps clearly

Next thought needed? (true/false)
    `;

    const result = await useMCPTool({
      server_name: this.thinkingServer,
      tool_name: 'sequentialthinking',
      arguments: {
        thought: thoughtPrompt,
        nextThoughtNeeded: thoughtNumber < totalThoughts,
        thoughtNumber,
        totalThoughts,
        isRevision: false
      }
    });

    return {
      number: thoughtNumber,
      content: result.thought,
      timestamp: new Date().toISOString(),
      contextSnapshot: { ...context },
      nextThoughtNeeded: result.nextThoughtNeeded || false,
      confidence: result.confidence || 0.8
    };
  }

  /**
   * อัปเดต context จาก thought
   * @param {Object} currentContext
   * @param {Object} thought
   * @returns {Promise<Object>}
   */
  async updateContextFromThought(currentContext, thought) {
    // Extract key insights from thought
    const insights = this.extractInsights(thought.content);
    
    // Update memory with new observations
    for (const insight of insights) {
      await this.addObservations(insight.entity, [insight.observation]);
    }
    
    // Update local context
    return {
      ...currentContext,
      insights: [...(currentContext.insights || []), ...insights],
      decisionHistory: [...(currentContext.decisionHistory || []), thought],
      lastUpdated: new Date().toISOString()
    };
  }

  /**
   * สร้าง final decision จาก sequential thinking
   * @param {Object} context
   * @returns {Promise<Object>}
   */
  async generateFinalDecision(context) {
    const decisionPrompt = `
Based on the sequential thinking process and memory graph, generate a final decision for the code review:

Context: ${JSON.stringify(context, null, 2)}

Requirements for final decision:
1. Clear recommendation: APPROVE, REJECT, or CONDITIONAL_APPROVAL
2. Detailed reasoning based on analysis
3. Specific action items with priorities
4. Risk assessment and mitigation strategies
5. Confidence level (0-1)
6. Fallback options if primary recommendation fails

Format:
{
  "recommendation": "APPROVE|REJECT|CONDITIONAL_APPROVAL",
  "reasoning": "detailed explanation in Thai",
  "actionItems": [{"priority": "high|medium|low", "description": "action", "responsible": "agent|manual"}],
  "riskAssessment": "risk level and mitigation",
  "confidence": 0.95,
  "fallbackOptions": ["alternative approaches"]
}
    `;

    const result = await useMCPTool({
      server_name: this.thinkingServer,
      tool_name: 'sequentialthinking',
      arguments: {
        thought: decisionPrompt,
        nextThoughtNeeded: false,
        thoughtNumber: 0,
        totalThoughts: 1,
        isRevision: false
      }
    });

    // Parse decision from result
    try {
      return JSON.parse(result.thought);
    } catch (error) {
      // Fallback parsing
      return {
        recommendation: 'CONDITIONAL_APPROVAL',
        reasoning: 'การตัดสินใจจาก sequential thinking process',
        actionItems: [],
        riskAssessment: 'medium risk with standard mitigations',
        confidence: 0.7,
        fallbackOptions: ['manual review', 'consult senior developer']
      };
    }
  }

  /**
   * Context-aware code review decision
   * @param {Object} codeReviewResult - ผลจาก CodeReviewAgent
   * @returns {Promise<Object>} Decision กับ reasoning
   */
  async makeContextAwareDecision(codeReviewResult) {
    try {
      console.log('🧠 Making context-aware decision...');
      
      // Load current project context from memory
      const projectContext = await this.loadProjectContext();
      
      // Perform sequential thinking
      const thinkingResult = await this.performSequentialThinking({
        codeReview: codeReviewResult,
        projectContext,
        timestamp: new Date().toISOString(),
        environment: process.env.NODE_ENV || 'development'
      });
      
      // Store decision in memory
      await this.storeDecision(codeReviewResult.filePath, thinkingResult);
      
      console.log(`✅ Decision made: ${thinkingResult.finalDecision.recommendation}`);
      
      return {
        ...thinkingResult.finalDecision,
        thinkingProcess: thinkingResult.thoughts,
        memoryContext: projectContext,
        agent: 'MemoryThinkingAgent'
      };
    } catch (error) {
      console.error('❌ Error in context-aware decision:', error.message);
      
      // Fallback to basic decision logic
      return this.fallbackDecision(codeReviewResult);
    }
  }

  /**
   * Fallback decision เมื่อ MCP tools ล้มเหลว
   * @param {Object} codeReviewResult
   * @returns {Object}
   */
  fallbackDecision(codeReviewResult) {
    console.log('🔄 Using fallback decision logic');
    
    const criticalCount = codeReviewResult.criticalIssues || 0;
    const totalIssues = codeReviewResult.totalIssues || 0;
    
    if (criticalCount > 0) {
      return {
        recommendation: 'REJECT',
        reasoning: 'พบ critical issues ที่ต้อง manual review ก่อน',
        actionItems: [
          {
            priority: 'high',
            description: 'ดำเนินการ manual code review สำหรับ critical issues',
            responsible: 'manual'
          }
        ],
        riskAssessment: 'high risk due to security/logic issues',
        confidence: 0.9,
        fallbackOptions: ['consult senior developer', 'security audit']
      };
    } else if (totalIssues > 5) {
      return {
        recommendation: 'CONDITIONAL_APPROVAL',
        reasoning: 'พบ non-critical issues หลายรายการ แนะนำ auto-fix',
        actionItems: [
          {
            priority: 'medium',
            description: 'Apply auto-fixes สำหรับ formatting และ style issues',
            responsible: 'agent'
          }
        ],
        riskAssessment: 'low risk, mostly cosmetic issues',
        confidence: 0.8,
        fallbackOptions: ['manual fix if auto-fix fails']
      };
    } else {
      return {
        recommendation: 'APPROVE',
        reasoning: 'Code quality อยู่ในเกณฑ์ดี ไม่พบปัญหาสำคัญ',
        actionItems: [],
        riskAssessment: 'minimal risk',
        confidence: 0.95,
        fallbackOptions: ['standard QA process']
      };
    }
  }

  /**
   * Load project context จาก memory
   * @returns {Promise<Object>}
   */
  async loadProjectContext() {
    try {
      const graph = await useMCPTool({
        server_name: this.memoryServer,
        tool_name: 'read_graph',
        arguments: {}
      });

      // Search for relevant context
      const relevantNodes = await useMCPTool({
        server_name: this.memoryServer,
        tool_name: 'search_nodes',
        arguments: { query: 'code review project context' }
      });

      return {
        graphSummary: graph,
        relevantNodes,
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      console.warn('⚠️  Could not load memory context, using default');
      return {
        graphSummary: { nodes: [], relations: [] },
        relevantNodes: [],
        lastUpdated: new Date().toISOString()
      };
    }
  }

  /**
   * Store decision ใน memory
   * @param {string} filePath
   * @param {Object} decision
   * @returns {Promise<void>}
   */
  async storeDecision(filePath, decision) {
    // Create entity for this decision
    await useMCPTool({
      server_name: this.memoryServer,
      tool_name: 'create_entities',
      arguments: {
        entities: [{
          name: `Decision_${filePath}_${Date.now()}`,
          entityType: 'Decision',
          observations: [
            `Decision for file ${filePath}`,
            `Recommendation: ${decision.finalDecision.recommendation}`,
            `Confidence: ${decision.finalDecision.confidence}`,
            `Timestamp: ${new Date().toISOString()}`
          ]
        }]
      }
    });

    // Add observations to CodeReviewProcess entity
    await this.addObservations('CodeReviewProcess', [
      `New decision recorded for ${filePath}: ${decision.finalDecision.recommendation}`,
      `Analysis completed with confidence ${decision.finalDecision.confidence}`
    ]);
  }

  /**
   * Extract insights จาก thought content
   * @param {string} thoughtContent
   * @returns {Array}
   */
  extractInsights(thoughtContent) {
    const insights = [];
    const entityPatterns = [
      { pattern: /entity: (\w+)/g, type: 'Entity' },
      { pattern: /relation: (\w+) between (.+) and (.+)/g, type: 'Relation' },
      { pattern: /observation: (.+)/g, type: 'Observation' }
    ];

    for (const patternInfo of entityPatterns) {
      let match;
      while ((match = patternInfo.pattern.exec(thoughtContent)) !== null) {
        insights.push({
          entity: match[1],
          type: patternInfo.type,
          observation: match[0],
          relevance: 0.8
        });
      }
    }

    return insights;
  }

  /**
   * คำนวณ confidence จาก thinking process
   * @returns {number}
   */
  calculateConfidence() {
    if (this.thoughtHistory.length === 0) return 0.5;
    
    const avgConfidence = this.thoughtHistory.reduce((sum, thought) => 
      sum + (thought.confidence || 0.7), 0
    ) / this.thoughtHistory.length;
    
    const consistencyScore = this.thoughtHistory.length > 1 ? 0.9 : 0.8;
    
    return Math.min(avgConfidence * consistencyScore, 1.0);
  }

  /**
   * Clear memory context (สำหรับ testing)
   * @returns {Promise<void>}
   */
  async clearMemory() {
    try {
      // Delete all entities (be careful in production)
      const entities = await useMCPTool({
        server_name: this.memoryServer,
        tool_name: 'read_graph',
        arguments: {}
      });

      if (entities && entities.entities) {
        const entityNames = entities.entities.map(e => e.name);
        await useMCPTool({
          server_name: this.memoryServer,
          tool_name: 'delete_entities',
          arguments: { entityNames }
        });
      }
      
      console.log('🧹 Memory cleared');
    } catch (error) {
      console.warn('⚠️  Could not clear memory:', error.message);
    }
  }
}

module.exports = MemoryThinkingAgent;