const { useMCPTool } = require('../services/mcp-toolbox');

class CodeReviewAgent {
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
   * ใช้ Codacy MCP tool สำหรับ linting และ security scanning
   * @param {string} filePath - เส้นทางไฟล์ที่ต้องการตรวจสอบ
   * @param {string} content - เนื้อหาไฟล์ (optional)
   * @returns {Promise<Object>} ผลการตรวจสอบ
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
   * รัน lint scan ด้วย Codacy
   * @param {string} filePath
   * @param {string} content
   * @returns {Promise<Object>}
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
   * รัน security scan ด้วย Codacy
   * @param {string} filePath
   * @param {string} content
   * @returns {Promise<Object>}
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
   * Classify issues เป็น critical หรือ non-critical
   * @param {Array} issues - รายการ issues
   * @returns {Promise<Object>}
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
   * กำหนดความรุนแรงของ issue
   * @param {Object} issue
   * @returns {Promise<string>} 'critical' หรือ 'non-critical'
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
   * สร้างคำแนะนำแก้ไขสำหรับ critical issues
   * @param {Object} issue
   * @returns {string}
   */
  generateCriticalFix(issue) {
    const fixes = {
      security: 'ต้องตรวจสอบและแก้ไขโดย manual review กับ security team',
      'breaking-change': 'ต้องอัปเดต API documentation และ migration scripts',
      'logic-error': 'ต้องทดสอบ unit tests เพิ่มเติมและ code review',
      'data-leak': 'ต้อง implement data encryption และ access controls'
    };
    
    return fixes[issue.type] || 'ต้อง manual review และ refactor code';
  }

  /**
   * สร้าง auto-fix สำหรับ non-critical issues
   * @param {Object} issue
   * @returns {Promise<string>}
   */
  async generateAutoFix(issue) {
    try {
      if (issue.category === 'formatting') {
        return 'prettier --write ${issue.file}';
      } else if (issue.category === 'style') {
        return 'eslint --fix ${issue.file}';
      } else if (issue.category === 'docs') {
        return `เพิ่ม JSDoc comment สำหรับ function ${issue.functionName}`;
      }
      
      return null;
    } catch (error) {
      console.warn(`⚠️  Cannot generate auto-fix for ${issue.message}`);
      return null;
    }
  }

  /**
   * Apply auto-fixes สำหรับ non-critical issues
   * @param {Array} nonCriticalIssues
   * @returns {Promise<Array>} รายการ fixes ที่ apply แล้ว
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
   * Generate review summary
   * @param {Object} classifiedIssues
   * @returns {string}
   */
  generateReviewSummary(classifiedIssues) {
    return `
📊 สรุปผลการตรวจสอบ Code Review:
• รวม issues: ${classifiedIssues.total}
• Critical issues (ต้อง manual review): ${classifiedIssues.critical}
• Non-critical issues (auto-fix ได้): ${classifiedIssues.nonCritical}

${classifiedIssues.needsManualReview ? '🚨 พบ critical issues ต้อง manual review' : '✅ ไม่พบ critical issues สามารถ proceed ได้'}

💡 คำแนะนำ:
${classifiedIssues.recommendations.slice(0, 3).map(r => `• ${r.description.substring(0, 50)}...`).join('\n')}
    `;
  }

  // Helper methods
  async readFileContent(filePath) {
    const fs = require('fs').promises;
    return await fs.readFile(filePath, 'utf8');
  }

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