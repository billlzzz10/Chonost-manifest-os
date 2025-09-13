const { useMCPTool } = require('../services/mcp-toolbox');

/**
 * @class CodeReviewAgent
 * @description An agent that performs code reviews using Codacy MCP tools.
 */
class CodeReviewAgent {
  /**
   * @param {object} [config={}] - The configuration for the agent.
   * @param {string} [config.token] - The Codacy account token.
   */
  constructor(config = {}) {
    this.serverName = 'codacy';
    this.config = {
      ...config,
      token: process.env.CODACY_ACCOUNT_TOKEN || config.token
    };
    this.isCritical = this.classifyIssueSeverity.bind(this);
    this.autoFix = this.applyAutoFixes.bind(this);
  }

  /**
   * Uses the Codacy MCP tool for linting and security scanning.
   * @param {string} filePath - The path to the file to review.
   * @param {string|null} [content=null] - The file content (optional).
   * @returns {Promise<Object>} The review result.
   */
  async performCodeReview(filePath, content = null) {
    try {
      console.log(`🔍 เริ่มตรวจสอบ code: ${filePath}`);
      
      const lintResult = await this.runLintScan(filePath, content);
      const securityResult = await this.runSecurityScan(filePath, content);
      
      const issues = [...(lintResult.issues || []), ...(securityResult.issues || [])];
      
      // Classify issues
      const classifiedIssues = await this.classifyIssues(issues);
      
      console.log(`✅ ตรวจสอบเสร็จสิ้น พบ ${classifiedIssues.total} issues`);
      
      return {
        filePath,
        totalIssues: classifiedIssues.total,
        criticalIssues: classifiedIssues.critical,
        nonCriticalIssues: classifiedIssues.nonCritical,
        summary: this.generateReviewSummary(classifiedIssues),
        recommendations: classifiedIssues.recommendations
      };
    } catch (error) {
      console.error(`❌ Error in code review: ${error.message}`);
      throw error;
    }
  }

  /**
   * Runs a lint scan using Codacy.
   * @param {string} filePath - The path to the file to scan.
   * @param {string} content - The content of the file.
   * @returns {Promise<Object>} The lint scan result.
   */
  async runLintScan(filePath, content) {
    try {
      const result = await useMCPTool({
        server_name: this.serverName,
        tool_name: 'lint',
        arguments: {
          file_path: filePath,
          content: content || await this.readFileContent(filePath),
          patterns: ['eslint', 'prettier', 'stylelint']
        }
      });
      
      return {
        type: 'lint',
        issues: result.issues || [],
        score: result.score || 0,
        warnings: result.warnings || []
      };
    } catch (error) {
      console.warn(`⚠️  Lint scan failed: ${error.message}`);
      return { type: 'lint', issues: [], score: 0 };
    }
  }

  /**
   * Runs a security scan using Codacy.
   * @param {string} filePath - The path to the file to scan.
   * @param {string} content - The content of the file.
   * @returns {Promise<Object>} The security scan result.
   */
  async runSecurityScan(filePath, content) {
    try {
      const result = await useMCPTool({
        server_name: this.serverName,
        tool_name: 'security-scan',
        arguments: {
          file_path: filePath,
          content: content || await this.readFileContent(filePath),
          severity: 'high,medium',
          patterns: ['sql-injection', 'xss', 'secrets', 'dependency-vuln']
        }
      });
      
      return {
        type: 'security',
        issues: result.vulnerabilities || [],
        riskScore: result.riskScore || 0,
        critical: result.critical || 0
      };
    } catch (error) {
      console.warn(`⚠️  Security scan failed: ${error.message}`);
      return { type: 'security', issues: [], riskScore: 0 };
    }
  }

  /**
   * Classifies issues as critical or non-critical.
   * @param {Array} issues - A list of issues.
   * @returns {Promise<Object>} An object with classified issues and recommendations.
   */
  async classifyIssues(issues) {
    const criticalTypes = ['security', 'breaking-change', 'logic-error', 'data-leak'];
    const nonCriticalTypes = ['style', 'formatting', 'docs', 'naming', 'comment'];
    
    let critical = 0, nonCritical = 0;
    const recommendations = [];
    
    for (const issue of issues) {
      const severity = await this.isCritical(issue);
      
      if (severity === 'critical') {
        critical++;
        recommendations.push({
          type: 'critical',
          description: issue.message,
          file: issue.file,
          line: issue.line,
          suggestion: this.generateCriticalFix(issue)
        });
      } else {
        nonCritical++;
        recommendations.push({
          type: 'non-critical',
          description: issue.message,
          file: issue.file,
          line: issue.line,
          autoFix: await this.generateAutoFix(issue)
        });
      }
    }
    
    return {
      total: issues.length,
      critical,
      nonCritical,
      recommendations,
      needsManualReview: critical > 0
    };
  }

  /**
   * Determines the severity of an issue.
   * @param {Object} issue - The issue object.
   * @returns {Promise<string>} 'critical' or 'non-critical'.
   */
  async classifyIssueSeverity(issue) {
    const criticalKeywords = ['security', 'vulnerability', 'injection', 'xss', 'sql', 'breaking', 'api-change', 'data-loss'];
    const securityTypes = ['secrets', 'auth', 'crypto', 'network'];
    
    // Check for security issues first
    if (issue.type && securityTypes.includes(issue.type.toLowerCase())) {
      return 'critical';
    }
    
    // Check keywords in message
    const message = (issue.message || '').toLowerCase();
    if (criticalKeywords.some(keyword => message.includes(keyword))) {
      return 'critical';
    }
    
    // Check for logic errors
    if (issue.category === 'logic' || issue.severity === 'high') {
      return 'critical';
    }
    
    return 'non-critical';
  }

  /**
   * Generates a fix recommendation for a critical issue.
   * @param {Object} issue - The issue object.
   * @returns {string} The fix recommendation.
   */
  generateCriticalFix(issue) {
    const fixes = {
      security: 'Requires manual review with the security team.',
      'breaking-change': 'Requires updating API documentation and migration scripts.',
      'logic-error': 'Requires additional unit tests and code review.',
      'data-leak': 'Requires implementing data encryption and access controls.'
    };
    
    return fixes[issue.type] || 'Requires manual review and code refactoring.';
  }

  /**
   * Generates an auto-fix command for a non-critical issue.
   * @param {Object} issue - The issue object.
   * @returns {Promise<string|null>} The auto-fix command or null.
   */
  async generateAutoFix(issue) {
    try {
      if (issue.category === 'formatting') {
        return 'prettier --write ${issue.file}';
      } else if (issue.category === 'style') {
        return 'eslint --fix ${issue.file}';
      } else if (issue.category === 'docs') {
        return `Add JSDoc comment for function ${issue.functionName}`;
      }
      
      return null;
    } catch (error) {
      console.warn(`⚠️  Cannot generate auto-fix for ${issue.message}`);
      return null;
    }
  }

  /**
   * Applies auto-fixes for non-critical issues.
   * @param {Array} nonCriticalIssues - A list of non-critical issues.
   * @returns {Promise<Array>} A list of applied fixes.
   */
  async applyAutoFixes(nonCriticalIssues) {
    const appliedFixes = [];
    
    for (const issue of nonCriticalIssues) {
      const fixCommand = await this.generateAutoFix(issue);
      
      if (fixCommand) {
        try {
          console.log(`🔧 Applying auto-fix: ${fixCommand}`);
          // Execute fix command (ใน production จะใช้ child_process)
          const result = await this.executeFix(fixCommand, issue.file);
          
          if (result.success) {
            appliedFixes.push({
              issue: issue.description,
              file: issue.file,
              command: fixCommand,
              status: 'fixed'
            });
            
            // Stage changes
            await this.stageChanges(issue.file);
          }
        } catch (error) {
          console.error(`❌ Auto-fix failed for ${issue.file}: ${error.message}`);
          appliedFixes.push({
            issue: issue.description,
            file: issue.file,
            status: 'fix_failed'
          });
        }
      }
    }
    
    return appliedFixes;
  }

  /**
   * Generates a review summary.
   * @param {Object} classifiedIssues - The classified issues object.
   * @returns {string} The review summary.
   */
  generateReviewSummary(classifiedIssues) {
    return `
📊 Code Review Summary:
• Total issues: ${classifiedIssues.total}
• Critical issues (manual review required): ${classifiedIssues.critical}
• Non-critical issues (auto-fixable): ${classifiedIssues.nonCritical}

${classifiedIssues.needsManualReview ? '🚨 Critical issues found, manual review required.' : '✅ No critical issues found, safe to proceed.'}

💡 Recommendations:
${classifiedIssues.recommendations.slice(0, 3).map(r => `• ${r.description.substring(0, 50)}...`).join('\n')}
    `;
  }

  // Helper methods
  /**
   * Reads the content of a file.
   * @param {string} filePath - The path to the file.
   * @returns {Promise<string>} The file content.
   * @private
   */
  async readFileContent(filePath) {
    const fs = require('fs').promises;
    return await fs.readFile(filePath, 'utf8');
  }

  /**
   * Executes a fix command.
   * @param {string} command - The command to execute.
   * @param {string} filePath - The path to the file.
   * @returns {Promise<Object>} The execution result.
   * @private
   */
  async executeFix(command, filePath) {
    const { exec } = require('child_process');
    return new Promise((resolve, reject) => {
      exec(command, { cwd: process.cwd() }, (error, stdout, stderr) => {
        if (error) {
          reject(error);
        } else {
          resolve({ success: true, output: stdout, file: filePath });
        }
      });
    });
  }

  /**
   * Stages changes in git.
   * @param {string} filePath - The path to the file to stage.
   * @private
   */
  async stageChanges(filePath) {
    const { execSync } = require('child_process');
    try {
      execSync(`git add ${filePath}`, { stdio: 'pipe' });
      console.log(`✅ Staged changes for ${filePath}`);
    } catch (error) {
      console.warn(`⚠️  Failed to stage ${filePath}`);
    }
  }
}

module.exports = CodeReviewAgent;