'use strict';

const fs = require('fs/promises');
const path = require('path');

const DEFAULT_TIMEOUT_MS = 5_000;
const CONFIG_FILENAME = 'mcp.json';

let cachedConfig = null;
let cachedConfigMtime = null;

const memoryState = {
  entities: new Map(),
  relations: []
};

function hasFetchSupport() {
  return typeof globalThis.fetch === 'function';
}

async function callFetch(url, options) {
  if (!hasFetchSupport()) {
    throw new Error('Fetch API is not available in this Node.js runtime.');
  }

  return globalThis.fetch(url, options);
}

function getRepoRoot() {
  return process.env.MCP_PROJECT_ROOT
    ? path.resolve(process.env.MCP_PROJECT_ROOT)
async function loadConfig() {
  const configPath = path.resolve(getRepoRoot(), CONFIG_FILENAME);

  let stat;
  try {
    stat = await fs.stat(configPath);
  } catch (error) {
    cachedConfig = { servers: {}, inputs: [] };
    cachedConfigMtime = null;
    if (process.env.MCP_TOOLBOX_DEBUG === 'true') {
      console.warn(`⚠️  Unable to load ${CONFIG_FILENAME}: ${error.message}`);
    }
    return cachedConfig;
  }

  if (cachedConfig && cachedConfigMtime === stat.mtimeMs) {
    return cachedConfig;
  }

  try {
    const raw = await fs.readFile(configPath, 'utf8');
    // Re-check mtime after reading to ensure consistency
    const postReadStat = await fs.stat(configPath);
    if (postReadStat.mtimeMs !== stat.mtimeMs) {
      // File was modified during read, retry once
      return loadConfig();
    }
    cachedConfig = JSON.parse(raw);
    cachedConfigMtime = postReadStat.mtimeMs;
  } catch (error) {
    cachedConfig = { servers: {}, inputs: [] };
    cachedConfigMtime = null;
    if (process.env.MCP_TOOLBOX_DEBUG === 'true') {
      console.warn(`⚠️  Unable to load ${CONFIG_FILENAME}: ${error.message}`);
    }
  }

  return cachedConfig;
}
    if (process.env.MCP_TOOLBOX_DEBUG === 'true') {
      console.warn(`⚠️  Unable to load ${CONFIG_FILENAME}: ${error.message}`);
    }
  }

  return cachedConfig;
}

async function getServerConfig(serverName) {
  if (!serverName) {
    throw new Error('server_name is required');
  }

  const config = await loadConfig();
  return config.servers && config.servers[serverName] ? { ...config.servers[serverName] } : null;
}

function sanitizeFilePath(filePath) {
  if (!filePath) {
    return null;
  }

  const repoRoot = getRepoRoot();
  const resolved = path.resolve(repoRoot, filePath);

  if (!resolved.startsWith(repoRoot)) {
    throw new Error(`Rejected unsafe file path: ${filePath}`);
  }

  return resolved;
}

async function resolveContent(args = {}) {
  if (typeof args.content === 'string' && args.content.trim().length > 0) {
    return args.content;
  }

  if (args.file_path) {
    const safePath = sanitizeFilePath(args.file_path);
    try {
      return await fs.readFile(safePath, 'utf8');
    } catch (error) {
      throw new Error(`Unable to read file for MCP tool: ${error.message}`);
    }
  }

  return '';
}

function buildIssue({
  type,
  message,
  line,
  file,
  severity = 'medium',
  category = 'general',
  suggestion = null
}) {
  return {
    type,
    message,
    line,
    file,
    severity,
    category,
    suggestion
  };
}

function analyseForLint(content, filePath) {
  const issues = [];
  const warnings = [];
  const lines = content.split(/\r?\n/);

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    const lineNumber = index + 1;

    if (trimmed.length === 0) {
      return;
    }

    if (/[^;{}\s]\s*$/.test(trimmed) && !/[,)]$/.test(trimmed) && /[a-zA-Z0-9_\)\]]$/.test(trimmed)) {
      issues.push(
        buildIssue({
          type: 'style',
          category: 'formatting',
          message: 'Missing semicolon at the end of the statement.',
          line: lineNumber,
          file: filePath,
          suggestion: 'Add a semicolon to terminate the statement.'
        })
      );
    }

    if (/TODO/i.test(trimmed)) {
      warnings.push(
        buildIssue({
          type: 'docs',
          category: 'docs',
          message: 'TODO comment detected. Ensure pending work is tracked.',
          line: lineNumber,
          file: filePath,
          suggestion: 'Resolve or track the TODO item explicitly.'
        })
      );
    }

    if (/console\.log\s*\(/.test(trimmed) && !/eslint-disable-next-line/.test(content)) {
      warnings.push(
        buildIssue({
          type: 'style',
          category: 'debug',
          message: 'console.log detected. Remove debug statements before committing.',
          line: lineNumber,
          file: filePath,
          suggestion: 'Remove or replace with a logger at the appropriate level.'
        })
      );
    }

    if (/var\s+/.test(trimmed)) {
      issues.push(
        buildIssue({
          type: 'style',
          category: 'convention',
          message: 'Avoid using var. Prefer const or let.',
          line: lineNumber,
          file: filePath,
          suggestion: 'Use const or let for variable declarations.'
        })
      );
    }

    if (/[ \t]+$/.test(line)) {
      warnings.push(
        buildIssue({
          type: 'style',
          category: 'formatting',
          message: 'Trailing whitespace detected.',
          line: lineNumber,
          file: filePath,
          suggestion: 'Remove trailing spaces.'
        })
      );
    }
  });

  const score = Math.max(0, 100 - issues.length * 10 - warnings.length * 2);

  return {
    type: 'lint',
    issues,
    warnings,
    score
  };
}

function analyseForSecurity(content, filePath) {
  const vulnerabilities = [];
  const lines = content.split(/\r?\n/);

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    const lineNumber = index + 1;

    if (/eval\s*\(/.test(trimmed)) {
      vulnerabilities.push(
        buildIssue({
          type: 'security',
          category: 'code-execution',
          message: 'Usage of eval detected. This can lead to remote code execution.',
          line: lineNumber,
          file: filePath,
          severity: 'critical',
          suggestion: 'Avoid eval and use safer alternatives.'
        })
      );
    }

    if (/child_process\.(exec|spawn|execFile)/.test(trimmed)) {
      vulnerabilities.push(
        buildIssue({
          type: 'security',
          category: 'command-execution',
          message: 'child_process execution detected. Ensure inputs are sanitized.',
          line: lineNumber,
          file: filePath,
          severity: 'high',
          suggestion: 'Validate and sanitize any input used for command execution.'
        })
      );
    }

    if (/process\.env\.[A-Z_]+/.test(trimmed) && /console\.log/.test(trimmed)) {
      vulnerabilities.push(
        buildIssue({
          type: 'security',
          category: 'secret-exposure',
          message: 'Logging environment variables can leak secrets.',
          line: lineNumber,
          file: filePath,
          severity: 'high',
          suggestion: 'Remove logging of sensitive configuration values.'
        })
      );
    }

    if (/password\s*=|secret\s*=|api_key\s*=|token\s*=/.test(trimmed.toLowerCase())) {
      vulnerabilities.push(
        buildIssue({
          type: 'security',
          category: 'hardcoded-secret',
          message: 'Potential hardcoded credential detected.',
          line: lineNumber,
          file: filePath,
          severity: 'critical',
          suggestion: 'Store secrets in environment variables or a secret manager.'
        })
      );
    }
  });

  const criticalCount = vulnerabilities.filter(v => v.severity === 'critical').length;
  const riskScore = vulnerabilities.length === 0 ? 0 : Math.min(100, 40 + vulnerabilities.length * 15);

  return {
    type: 'security',
    vulnerabilities,
    issues: vulnerabilities,
    critical: criticalCount,
    riskScore
  };
}

function ensureMemoryEntity(name, entityType = 'Unknown') {
  if (!memoryState.entities.has(name)) {
    memoryState.entities.set(name, {
      name,
      entityType,
      observations: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    });
  }

  return memoryState.entities.get(name);
}

function memoryToolHandler(toolName, args = {}) {
  switch (toolName) {
    case 'create_entities': {
      const entities = Array.isArray(args.entities) ? args.entities : [];
      const created = [];
      entities.forEach(entity => {
        if (!entity || !entity.name) {
          return;
        }

        const stored = ensureMemoryEntity(entity.name, entity.entityType || 'Unknown');
        if (Array.isArray(entity.observations) && entity.observations.length > 0) {
          stored.observations.push(...entity.observations);
        }
        stored.updatedAt = new Date().toISOString();
        created.push(stored.name);
      });
      return { status: 'ok', created };
    }
    case 'create_relations': {
      const relations = Array.isArray(args.relations) ? args.relations : [];
      const storedRelations = [];
      relations.forEach(relation => {
        if (!relation || !relation.from || !relation.to) {
          return;
        }

        memoryState.relations.push({
          from: relation.from,
          to: relation.to,
          relationType: relation.relationType || 'related_to',
          createdAt: new Date().toISOString()
        });
        storedRelations.push(relation);
      });
      return { status: 'ok', relations: storedRelations.length };
    }
    case 'add_observations': {
      const observations = Array.isArray(args.observations) ? args.observations : [];
      const updated = [];
      observations.forEach(entry => {
        if (!entry || !entry.entityName) {
          return;
        }
        const entity = ensureMemoryEntity(entry.entityName);
        if (Array.isArray(entry.contents)) {
          entity.observations.push(...entry.contents);
          entity.updatedAt = new Date().toISOString();
          updated.push(entry.entityName);
        }
      });
      return { status: 'ok', updated };
    }
    case 'read_graph': {
      return {
        entities: Array.from(memoryState.entities.values()),
        relations: [...memoryState.relations]
      };
    }
    case 'search_nodes': {
      const query = (args.query || '').toLowerCase();
      const matches = Array.from(memoryState.entities.values()).filter(entity => {
        if (entity.name.toLowerCase().includes(query)) {
          return true;
        }

        return entity.observations.some(obs => obs.toLowerCase().includes(query));
      });

      return matches.map(entity => ({
        name: entity.name,
        entityType: entity.entityType,
        observations: entity.observations.slice(-5),
        score: Math.min(1, 0.6 + entity.observations.length * 0.05)
      }));
    }
    case 'delete_entities': {
      const names = Array.isArray(args.entityNames) ? args.entityNames : [];
      names.forEach(name => memoryState.entities.delete(name));
      memoryState.relations = memoryState.relations.filter(
        relation => !names.includes(relation.from) && !names.includes(relation.to)
      );
      return { status: 'ok', deleted: names.length };
    }
    default:
      return { status: 'unsupported', tool: toolName };
  }
}

function summariseContext(context = {}) {
  const summary = [];

  if (context.codeReview) {
    const review = context.codeReview;
    summary.push(
      `entity: CodeReviewProcess`,
      `observation: Critical issues ${review.criticalIssues || 0}`,
      `observation: Total issues ${review.totalIssues || 0}`
    );
  }

  if (context.environment) {
    summary.push(`observation: Environment ${context.environment}`);
  }

  if (context.projectContext && context.projectContext.name) {
    summary.push(`entity: Project_${context.projectContext.name.replace(/[^A-Za-z0-9]/g, '')}`);
  }

  return summary;
}

function sequentialThinkingHandler(args = {}) {
  const prompt = args.thought || '';
  const thoughtNumber = typeof args.thoughtNumber === 'number' ? args.thoughtNumber : 1;
  const totalThoughts = typeof args.totalThoughts === 'number' ? args.totalThoughts : 1;
  const baseConfidence = 0.75;
  let context = {};

  const contextMatch = prompt.match(/Context:\s*(\{[\s\S]*?\})\s*Requirements/);
  if (contextMatch) {
    try {
      context = JSON.parse(contextMatch[1]);
    } catch (error) {
      context = {};
    }
  }

  if (/"recommendation"/.test(prompt) && /"actionItems"/.test(prompt)) {
    const review = context.codeReview || context;
    const critical = review.criticalIssues || 0;
    const total = review.totalIssues || 0;
    const recommendation = critical > 0 ? 'REJECT' : total > 5 ? 'CONDITIONAL_APPROVAL' : 'APPROVE';

    const actionItems = [];
    if (critical > 0) {
      actionItems.push({
        priority: 'high',
        description: 'ดำเนินการตรวจสอบโค้ดเชิงลึกสำหรับ critical issues',
        responsible: 'manual'
      });
    } else if (total > 0) {
      actionItems.push({
        priority: 'medium',
        description: 'ใช้ auto-fix สำหรับ non-critical issues และตรวจสอบซ้ำ',
        responsible: 'agent'
      });
    }

    const confidence = critical > 0 ? 0.78 : total > 5 ? 0.82 : 0.9;

    const decision = {
      recommendation,
      reasoning:
        recommendation === 'APPROVE'
          ? 'ไม่พบปัญหาร้ายแรงและคุณภาพโค้ดอยู่ในเกณฑ์ที่ยอมรับได้'
          : recommendation === 'CONDITIONAL_APPROVAL'
          ? 'พบปัญหาเล็กน้อยจำนวนมาก ควรแก้ไขอัตโนมัติและตรวจสอบซ้ำ'
          : 'พบประเด็นที่มีความเสี่ยงสูง จำเป็นต้องหยุดเพื่อทำการตรวจสอบเชิงลึก',
      actionItems,
      riskAssessment:
        recommendation === 'APPROVE'
          ? 'minimal risk'
          : recommendation === 'CONDITIONAL_APPROVAL'
          ? 'medium risk, requires follow-up'
          : 'high risk until issues resolved',
      confidence,
      fallbackOptions:
        recommendation === 'APPROVE'
          ? ['standard QA process']
          : ['manual review', 'consult senior developer']
    };

    return {
      thought: JSON.stringify(decision, null, 2),
      nextThoughtNeeded: false,
      confidence: decision.confidence
    };
  }

  const summary = summariseContext(context);
  const keyActions = [];

  if (context.codeReview) {
    const review = context.codeReview;
    if (review.criticalIssues > 0) {
      keyActions.push('ระบุ critical issues ที่ต้องแก้ไขทันที');
    }
    if ((review.nonCriticalIssues || 0) > 0) {
      keyActions.push('จัดลำดับ non-critical issues สำหรับ auto-fix');
    }
  }

  if (summary.length === 0) {
    summary.push('observation: ไม่มี context ที่ระบุอย่างชัดเจน');
  }

  const nextThoughtNeeded = typeof args.nextThoughtNeeded === 'boolean'
    ? args.nextThoughtNeeded && thoughtNumber < totalThoughts
    : thoughtNumber < totalThoughts;

  const content = [
    `Thought ${thoughtNumber}/${totalThoughts}`,
    ...summary,
    'analysis: ประเมินผลกระทบของปัญหาและความเสี่ยง',
    ...keyActions.map(action => `observation: ${action}`),
    `next: ${nextThoughtNeeded ? 'ต้องการการวิเคราะห์ต่อ' : 'พร้อมสรุปการตัดสินใจ'}`
  ].join('\n');

  return {
    thought: content,
    nextThoughtNeeded,
    confidence: Math.min(1, baseConfidence + summary.length * 0.03)
  };
}

async function attemptHttpCall(serverConfig, toolName, args) {
  if (!serverConfig.url) {
    return null;
  }

  if (!hasFetchSupport()) {
    return null;
  }

  const endpoint = serverConfig.url.endsWith('/')
    ? `${serverConfig.url}tools/${encodeURIComponent(toolName)}`
    : `${serverConfig.url}/tools/${encodeURIComponent(toolName)}`;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), args.timeoutMs || DEFAULT_TIMEOUT_MS);

  try {
    const response = await callFetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(serverConfig.headers || {})
      },
      body: JSON.stringify({ arguments: args }),
      signal: controller.signal
    });

    clearTimeout(timeout);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      return await response.json();
    }

    return { result: await response.text() };
  } catch (error) {
    clearTimeout(timeout);
    if (process.env.MCP_TOOLBOX_DEBUG === 'true') {
      console.warn(`⚠️  HTTP MCP call failed for ${toolName}: ${error.message}`);
    }
    return null;
  }
}

async function runMockTool(serverName, toolName, args) {
  switch (serverName) {
    case 'codacy': {
      if (toolName === 'lint') {
        const content = await resolveContent(args);
        return analyseForLint(content, args.file_path || 'virtual-file.js');
      }
      if (toolName === 'security-scan') {
        const content = await resolveContent(args);
        return analyseForSecurity(content, args.file_path || 'virtual-file.js');
      }
      if (toolName === 'health-check') {
        return {
          status: 'healthy',
          provider: 'mock',
          timestamp: new Date().toISOString()
        };
      }
      return { status: 'unsupported', tool: toolName };
    }
    case 'memory':
      return memoryToolHandler(toolName, args);
    case 'sequentialthinking':
      if (toolName === 'sequentialthinking') {
        return sequentialThinkingHandler(args);
      }
      return { status: 'unsupported', tool: toolName };
    default:
      return {
        status: 'not_configured',
        server: serverName,
        tool: toolName
      };
  }
}

async function useMCPTool({ server_name: serverName, tool_name: toolName, arguments: args = {} } = {}) {
  if (!serverName) {
    throw new Error('server_name is required');
  }
  if (!toolName) {
    throw new Error('tool_name is required');
  }

  const serverConfig = await getServerConfig(serverName);

  if (serverConfig && serverConfig.type === 'http') {
    const httpResult = await attemptHttpCall(serverConfig, toolName, args);
    if (httpResult) {
      return httpResult;
    }
  }

  if (
    serverConfig &&
    ['stdio', 'command'].includes(serverConfig.type || '') &&
    process.env.MCP_TOOLBOX_ALLOW_SPAWN === 'true'
  ) {
    // Intentionally not implemented for safety. Production users can extend this section.
    console.warn(
      '⚠️  STDIO MCP execution is disabled by default. Remove MCP_TOOLBOX_ALLOW_SPAWN or set it to false to silence this warning.'
    );
  }

  return runMockTool(serverName, toolName, args);
}

async function accessMCPResource({
  server_name: serverName,
  resource_path: resourcePath = '',
  method = 'GET',
  body = null,
  headers = {},
  timeoutMs = DEFAULT_TIMEOUT_MS
} = {}) {
  if (!serverName) {
    throw new Error('server_name is required');
  }

  const serverConfig = await getServerConfig(serverName);
  if (!serverConfig || serverConfig.type !== 'http' || !serverConfig.url) {
    throw new Error(`Server ${serverName} does not expose HTTP resources.`);
  }

  const baseUrl = serverConfig.url.endsWith('/') ? serverConfig.url : `${serverConfig.url}/`;
  const url = new URL(resourcePath, baseUrl);

  if (!hasFetchSupport()) {
    throw new Error('Fetch API is not available in this Node.js runtime.');
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await callFetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(serverConfig.headers || {}),
        ...headers
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal
    });

    clearTimeout(timeout);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      return await response.json();
    }
    return await response.text();
  } catch (error) {
    clearTimeout(timeout);
    throw new Error(`Failed to access MCP resource: ${error.message}`);
  }
}

function resetMockState() {
  memoryState.entities.clear();
  memoryState.relations = [];
}

module.exports = {
  loadMCPConfig: loadConfig,
  getMCPServerConfig: getServerConfig,
  useMCPTool,
  accessMCPResource,
  resetMockState
};
