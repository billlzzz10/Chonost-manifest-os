const OpenAI = require('openai');
const config = require('../config/ai-commit.config');
const { getGitDiff } = require('./git-utils');
const CodeReviewAgent = require('../agents/code-review-agent');
const MemoryThinkingAgent = require('../agents/memory-thinking-agent');
const { useMCPTool } = require('../services/mcp-toolbox'); // MCP integration service

class AICommitManager {
  constructor(type = 'commit') {
    this.type = type;
    this.config = config[type];
    if (!this.config.apiKey) {
      throw new Error('API key not found. Please set OPENROUTER_API_KEY environment variable.');
    }
    
    this.openai = new OpenAI({
      apiKey: this.config.apiKey,
      baseURL: this.config.baseUrl
    });

    // Initialize MCP integration and agents
    this.mcpAvailable = false;
    this.initializeMCP().catch(console.error);
    
    // Initialize review agents
    this.codeReviewAgent = new CodeReviewAgent({
      token: process.env.CODACY_ACCOUNT_TOKEN
    });
    
    this.memoryAgent = new MemoryThinkingAgent({
      memoryFilePath: './memory-review.json'
    });
    
    this.reviewEnabled = process.env.ENABLE_AI_REVIEW === 'true';
  }

  /**
   * Initialize MCP connection and tools
   * @returns {Promise<void>}
   */
  async initializeMCP() {
    try {
      console.log('🔌 Initializing MCP integration...');
      
      // Test MCP connection
      const testResult = await useMCPTool({
        server_name: 'codacy',
        tool_name: 'health-check',
        arguments: {}
      });
      
      if (testResult && testResult.status === 'healthy') {
        this.mcpAvailable = true;
        console.log('✅ MCP integration successful');
        
        // Initialize memory agent
        await this.memoryAgent.initializeMemoryGraph();
      } else {
        console.warn('⚠️  MCP not available, using fallback mechanisms');
      }
    } catch (error) {
      console.warn(`⚠️  MCP initialization failed: ${error.message}`);
      this.mcpAvailable = false;
    }
  }

  /**
   * Generate content with fallback mechanism
   * @param {string} prompt - User prompt
   * @param {string} systemPrompt - System prompt (optional)
   * @returns {Promise<string>} Generated content
   */
  async generateWithFallback(prompt, systemPrompt = null) {
    const models = [this.config.model, ...this.config.fallbackModels];
    let lastError = null;
    
    console.log(`🤖 Trying to generate with ${models.length} models...`);
    
    for (const model of models) {
      try {
        console.log(`🔄 Trying model: ${model}`);
        
        const response = await this.openai.chat.completions.create({
          model: model,
          messages: [
            ...(systemPrompt ? [{ role: 'system', content: systemPrompt }] : []),
            { role: 'user', content: prompt }
          ],
          max_tokens: 200,
          temperature: 0.7
        });
        
        const content = response.choices[0].message.content.trim();
        console.log(`✅ Successfully generated with ${model}`);
        return content;
        
      } catch (error) {
        lastError = error;
        console.log(`❌ Model ${model} failed: ${error.message}`);
        continue;
      }
    }
    
    throw new Error(`All AI models failed. Last error: ${lastError.message}`);
  }

  /**
   * Enhanced commit message generation with AI review
   * @returns {Promise<{message: string, reviewResult: Object, status: string}>} Commit message with review results
   */
  async generateCommitMessage() {
    const diff = getGitDiff();
    
    if (!diff || diff.trim() === '') {
      throw new Error('No staged changes found. Please stage your changes first.');
    }
    
    console.log('🚀 Starting enhanced AI commit workflow...');
    
    let reviewResult = null;
    let finalStatus = 'APPROVED';
    
    // Step 1: Perform AI code review if enabled
    if (this.reviewEnabled) {
      reviewResult = await this.performAIReview(diff);
      
      console.log('📊 Review Summary:');
      console.log(reviewResult.summary);
      
      // Step 2: Handle critical vs non-critical issues
      if (reviewResult.needsManualReview) {
        console.log('🚨 Critical issues detected - pausing for manual review');
        
        // Use memory agent for context-aware decision
        const decision = await this.memoryAgent.makeContextAwareDecision(reviewResult);
        
        if (decision.recommendation === 'REJECT') {
          console.log('❌ Commit rejected due to critical issues');
          finalStatus = 'REJECTED';
          
          // Provide detailed remediation paths
          this.printRemediationPaths(reviewResult, decision);
          return {
            message: '',
            reviewResult,
            status: finalStatus,
            decision,
            requiresManualReview: true
          };
        } else if (decision.recommendation === 'CONDITIONAL_APPROVAL') {
          console.log('⚠️  Conditional approval - proceeding with warnings');
          finalStatus = 'CONDITIONAL';
        }
      } else {
        // Handle non-critical issues - auto-fix
        console.log('🔧 Applying auto-fixes for non-critical issues...');
        const fixesApplied = await this.applyNonCriticalFixes(reviewResult);
        console.log(`✅ Applied ${fixesApplied.length} auto-fixes`);
        
        // Stage fixed files
        await this.stageFixedFiles(fixesApplied);
      }
    }
    
    // Step 3: Generate commit message
    console.log('📝 Generating commit message from git diff...');
    const commitMessage = await this.generateEnhancedCommitMessage(diff, reviewResult);
    
    // Step 4: Final decision with memory agent if MCP available
    if (this.mcpAvailable && reviewResult) {
      const finalDecision = await this.memoryAgent.makeContextAwareDecision({
        ...reviewResult,
        commitMessage,
        status: finalStatus
      });
      
      if (finalDecision.recommendation === 'APPROVE') {
        finalStatus = 'APPROVED';
      } else {
        finalStatus = 'REQUIRES_REVIEW';
      }
    }
    
    console.log(`🎯 Final status: ${finalStatus}`);
    
    return {
      message: commitMessage,
      reviewResult,
      status: finalStatus,
      fixesApplied: reviewResult ? reviewResult.appliedFixes : []
    };
  }

  /**
   * Perform AI code review using CodeReviewAgent
   * @param {string} diff - Git diff content
   * @returns {Promise<Object>} Review results
   */
  async performAIReview(diff) {
    try {
      console.log('🔍 Starting AI code review...');
      
      // Extract changed files from diff
      const changedFiles = this.extractChangedFiles(diff);
      console.log(`📁 Found ${changedFiles.length} changed files`);
      
      const reviewResults = [];
      let totalCritical = 0, totalNonCritical = 0;
      
      for (const filePath of changedFiles) {
        try {
          // Read file content
          const fileContent = await this.readFileContent(filePath);
          
          // Perform code review
          const fileReview = await this.codeReviewAgent.performCodeReview(filePath, fileContent);
          reviewResults.push(fileReview);
          
          totalCritical += fileReview.criticalIssues;
          totalNonCritical += fileReview.nonCriticalIssues;
          
          console.log(`✅ Reviewed ${filePath}: ${fileReview.criticalIssues} critical, ${fileReview.nonCriticalIssues} non-critical`);
        } catch (error) {
          console.warn(`⚠️  Failed to review ${filePath}: ${error.message}`);
        }
      }
      
      const summary = this.generateReviewSummary({
        totalFiles: changedFiles.length,
        totalCritical,
        totalNonCritical,
        needsManualReview: totalCritical > 0,
        reviewedFiles: reviewResults.length
      });
      
      // Apply auto-fixes for non-critical issues
      const appliedFixes = [];
      for (const result of reviewResults) {
        if (result.nonCriticalIssues > 0) {
          const fixes = await this.codeReviewAgent.applyAutoFixes(
            result.recommendations.filter(r => r.type === 'non-critical')
          );
          appliedFixes.push(...fixes);
        }
      }
      
      return {
        summary,
        totalCritical,
        totalNonCritical,
        needsManualReview: totalCritical > 0,
        changedFiles,
        reviewResults,
        appliedFixes,
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      console.error('❌ AI review failed:', error.message);
      return {
        summary: 'AI review unavailable - proceeding with basic analysis',
        totalCritical: 0,
        totalNonCritical: 0,
        needsManualReview: false,
        changedFiles: [],
        reviewResults: [],
        appliedFixes: [],
        error: error.message
      };
    }
  }

  /**
   * Generate enhanced commit message with review context
   * @param {string} diff
   * @param {Object} reviewResult
   * @returns {Promise<string>}
   */
  async generateEnhancedCommitMessage(diff, reviewResult = null) {
    let basePrompt = `Generate a GitHub Actions style commit message with emojis for this git diff:
 
${diff}
 
Requirements:
- Use GitHub Actions format with emojis (🚀 feat:, 🐛 fix:, 📝 docs:, etc.)
- Keep it concise and descriptive
- Use Thai language for the message content
- Maximum 72 characters per line
- Include relevant emoji that matches the change type`;

    let systemPrompt = `You are a helpful assistant that generates GitHub Actions style commit messages with emojis.
You are an expert software developer who writes clear, concise commit messages.
You use Thai language for the message content and follow GitHub Actions format with emojis.
 
Common emoji mappings:
- 🚀 feat: New features
- 🐛 fix: Bug fixes
- 📝 docs: Documentation
- 💄 style: Code style changes
- 🎨 refactor: Code refactoring
- ⚡ perf: Performance improvements
- 🧪 test: Tests
- 🔧 build: Build system
- 📦 chore: Maintenance
- ✨ new: New additions
- 🚨 security: Security fixes`;

    // Enhance prompt with review context if available
    if (reviewResult && !reviewResult.error) {
      const reviewInfo = `
AI Review Results:
- Critical issues: ${reviewResult.totalCritical}
- Non-critical issues: ${reviewResult.totalNonCritical}
- Auto-fixes applied: ${reviewResult.appliedFixes.length}
- Status: ${reviewResult.needsManualReview ? 'Manual review required' : 'Auto-approved'}`;

      basePrompt += `\n\n${reviewInfo}\n\nInclude review status in the commit message if relevant.`;
      
      systemPrompt += `\n\nYou have access to AI code review results. Consider the review findings when generating the commit message. If critical issues were found, include a note about manual review. If auto-fixes were applied, mention code quality improvements.`;
    }

    return this.generateWithFallback(basePrompt, systemPrompt);
  }

  /**
   * Extract changed files from git diff
   * @param {string} diff
   * @returns {Array<string>}
   */
  extractChangedFiles(diff) {
    const files = [];
    const fileLines = diff.split('\n').filter(line =>
      line.startsWith('+++') && !line.includes('/dev/null')
    );
    
    for (const line of fileLines) {
      const match = line.match(/^\+\+\+ b\/(.+)$/);
      if (match) {
        files.push(match[1]);
      }
    }
    
    return files;
  }

  /**
   * Generate review summary
   * @param {Object} stats
   * @returns {string}
   */
  generateReviewSummary(stats) {
    return `AI Code Review Summary:
📁 Files reviewed: ${stats.totalFiles}
🚨 Critical issues: ${stats.totalCritical} (requires manual review)
⚠️  Non-critical issues: ${stats.totalNonCritical} (auto-fixed)
✅ Successfully reviewed: ${stats.reviewedFiles} files
${stats.needsManualReview ? '🔴 MANUAL REVIEW REQUIRED' : '🟢 READY FOR COMMIT'}`;
  }

  /**
   * Apply non-critical fixes
   * @param {Object} reviewResult
   * @returns {Promise<Array>}
   */
  async applyNonCriticalFixes(reviewResult) {
    const allFixes = [];
    
    for (const fileReview of reviewResult.reviewResults) {
      if (fileReview.nonCriticalIssues > 0) {
        const fixes = await this.codeReviewAgent.applyAutoFixes(
          fileReview.recommendations.filter(r => r.type === 'non-critical')
        );
        allFixes.push(...fixes);
      }
    }
    
    return allFixes;
  }

  /**
   * Stage fixed files
   * @param {Array} fixesApplied
   * @returns {Promise<void>}
   */
  async stageFixedFiles(fixesApplied) {
    const { execSync } = require('child_process');
    const fs = require('fs');
    
    const fixedFiles = [...new Set(fixesApplied.map(fix => fix.file).filter(Boolean))];
    
    for (const file of fixedFiles) {
      if (fs.existsSync(file)) {
        try {
          execSync(`git add "${file}"`, { stdio: 'pipe' });
          console.log(`✅ Staged fixed file: ${file}`);
        } catch (error) {
          console.warn(`⚠️  Failed to stage ${file}: ${error.message}`);
        }
      }
    }
  }

  /**
   * Print remediation paths for critical issues
   * @param {Object} reviewResult
   * @param {Object} decision
   */
  printRemediationPaths(reviewResult, decision) {
    console.log('\n🚨 CRITICAL ISSUES DETECTED - REMEDIATION PATHS:');
    console.log('=' .repeat(60));
    
    for (const fileReview of reviewResult.reviewResults) {
      for (const issue of fileReview.recommendations.filter(r => r.type === 'critical')) {
        console.log(`\n📄 File: ${issue.file}`);
        console.log(`🚨 Issue: ${issue.description}`);
        console.log(`💡 Recommendation: ${issue.suggestion}`);
        console.log(`🎯 Priority: High - Manual Review Required`);
      }
    }
    
    console.log('\n📋 ACTION ITEMS FROM AI ANALYSIS:');
    for (const action of decision.actionItems) {
      console.log(`• [${action.priority.toUpperCase()}] ${action.description}`);
      console.log(`  Responsible: ${action.responsible === 'manual' ? 'Developer' : 'AI Agent'}`);
    }
    
    console.log('\n⚠️  COMMIT PAUSED - Please address critical issues before proceeding');
    console.log('💡 Use: git commit --no-verify to bypass review (not recommended)');
  }

  /**
   * Read file content helper
   * @param {string} filePath
   * @returns {Promise<string>}
   */
  async readFileContent(filePath) {
    const fs = require('fs').promises;
    try {
      return await fs.readFile(filePath, 'utf8');
    } catch (error) {
      console.warn(`⚠️  Could not read file ${filePath}: ${error.message}`);
      return '';
    }
  }

  /**
   * Determine version bump type based on commits
   * @param {string[]} commits - Array of commit messages
   * @returns {Promise<string>} Version bump type (major, minor, patch)
   */
  async determineVersionBump(commits) {
    if (!commits || commits.length === 0) {
      throw new Error('No commits found to analyze.');
    }
    
    console.log('🔍 Analyzing commits for version bump...');
    
    const prompt = `Analyze these commit messages and determine if this is a major, minor, or patch version bump.
Respond with ONLY one word: major, minor, or patch

Recent commits:
${commits.map((commit, index) => `${index + 1}. ${commit}`).join('\n')}

Version bump rules:
- MAJOR: Breaking changes, new major features that change API
- MINOR: New features, backward-compatible enhancements
- PATCH: Bug fixes, documentation, minor improvements`;

    const systemPrompt = `You are a version management expert. Analyze commit messages and determine the appropriate version bump type.
You understand semantic versioning and can identify:
- Breaking changes that require major version bump
- New features that require minor version bump  
- Bug fixes and minor improvements that require patch version bump

Respond with ONLY: major, minor, or patch`;

    return this.generateWithFallback(prompt, systemPrompt);
  }

  /**
   * Generate release notes from commits
   * @param {string[]} commits - Array of commit messages
   * @returns {Promise<string>} Generated release notes
   */
  async generateReleaseNotes(commits) {
    console.log('📋 Generating release notes...');
    
    const prompt = `Generate comprehensive release notes in Thai language for these commits:

${commits.map((commit, index) => `${index + 1}. ${commit}`).join('\n')}

Requirements:
- Write in Thai language
- Group similar changes together
- Use clear and descriptive language
- Include version number placeholder [VERSION]
- Keep it professional but friendly
- Maximum 200 words`;

    const systemPrompt = `You are a technical writer who creates professional release notes.
You write in Thai language and can organize technical information clearly.
You create release notes that are informative yet easy to understand for both technical and non-technical users.`;

    return this.generateWithFallback(prompt, systemPrompt);
  }
}

// Export for use in other modules
module.exports = AICommitManager;

// CLI usage
if (require.main === module) {
  const manager = new AICommitManager();
  
  async function main() {
    try {
      const action = process.argv[2];
      
      switch (action) {
        case 'commit':
          const result = await manager.generateCommitMessage();
          
          if (result.status === 'APPROVED' || result.status === 'CONDITIONAL') {
            console.log('🎯 Generated commit message:');
            console.log(result.message);
            
            if (result.reviewResult && result.reviewResult.appliedFixes.length > 0) {
              console.log('\n🔧 Auto-fixes applied:');
              result.reviewResult.appliedFixes.forEach(fix => {
                console.log(`  • ${fix.status}: ${fix.issue.substring(0, 50)}...`);
              });
            }
            
            // Write to COMMIT_EDITMSG if in hook context
            if (process.env.GIT_HOOK) {
              const fs = require('fs');
              fs.writeFileSync('.git/COMMIT_EDITMSG', result.message);
              console.log('\n✅ Commit message written to .git/COMMIT_EDITMSG');
            }
          } else {
            console.log('❌ Commit rejected by AI review');
            console.log(`Status: ${result.status}`);
            if (result.decision) {
              console.log(`AI Decision: ${result.decision.recommendation}`);
              console.log(`Reason: ${result.decision.reasoning}`);
            }
            process.exit(1);
          }
          break;
          
        case 'version':
          const commits = require('./git-utils').getRecentCommits(10);
          const versionType = await manager.determineVersionBump(commits);
          console.log(`📦 Recommended version bump: ${versionType}`);
          break;
          
        case 'release':
          const recentCommits = require('./git-utils').getRecentCommits(10);
          const releaseNotes = await manager.generateReleaseNotes(recentCommits);
          console.log('📝 Release notes:');
          console.log(releaseNotes);
          break;
          
        default:
          console.log('Usage:');
          console.log('  node scripts/ai-commit.js commit    # Generate commit message');
          console.log('  node scripts/ai-commit.js version   # Determine version bump');
          console.log('  node scripts/ai-commit.js release   # Generate release notes');
      }
    } catch (error) {
      console.error('❌ Error:', error.message);
      process.exit(1);
    }
  }
  
  main();
}