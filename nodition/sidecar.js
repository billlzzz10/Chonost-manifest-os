/**
 * Nodition Sidecar - Backend service for Notion integration
 * Runs notion.py script via child_process and handles communication
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const { EventEmitter } = require('events');

class NotionSidecar extends EventEmitter {
  constructor() {
    super();
    this.pythonProcess = null;
    this.isRunning = false;
    this.outputBuffer = [];
    this.errorBuffer = [];
    
    // Ensure scripts directory exists
    const scriptsDir = path.join(__dirname, '../scripts');
    if (!fs.existsSync(scriptsDir)) {
      fs.mkdirSync(scriptsDir, { recursive: true });
    }
  }

  /**
   * Start Notion sync process
   * @param {Object} options - Sync options
   * @param {boolean} options.syncVault - Sync data to manuscript vault
   * @param {string} options.notionToken - Notion API token
   * @param {string} options.vaultPath - Manuscript vault path
   * @returns {Promise} Process start promise
   */
  async startNotionSync(options = {}) {
    return new Promise((resolve, reject) => {
      if (this.isRunning) {
        this.emit('warning', 'Notion sync is already running');
        resolve({ status: 'already_running' });
        return;
      }
  
      // Default options with manifest generation
      const config = {
        syncVault: true,
        generateManifest: options.generateManifest !== false, // Default to true
        notionToken: process.env.NOTION_TOKEN || '',
        vaultPath: process.env.MANUSCRIPT_VAULT || './manuscript-vault',
        ...options
      };
  
      console.log('🚀 Starting Notion sync process...');
      console.log('📁 Vault path:', config.vaultPath);
      console.log('🔄 Sync vault:', config.syncVault);
      console.log('📋 Generate manifest:', config.generateManifest);
  
      // Build command line arguments for notion.py
      const args = ['notion.py'];
      if (config.syncVault) {
        args.push('--sync-vault');
      }
      
      if (config.generateManifest) {
        args.push('--generate-dual-identity');
      }
      
      if (config.notionToken) {
        args.push('--token', config.notionToken);
      }
      
      if (config.vaultPath) {
        args.push('--vault', config.vaultPath);
      }

      // Find Python executable
      let pythonExec = 'python';
      if (process.platform === 'win32') {
        pythonExec = 'python.exe';
      }

      // Try to find Python in PATH first, then check common locations
      const pythonPaths = [
        pythonExec,
        'python3',
        path.join(process.env.VIRTUAL_ENV || '', 'Scripts', 'python.exe'),
        'C:\\Python39\\python.exe',
        '/usr/bin/python3'
      ];

      let pythonPath = null;
      let found = false;
      for (const p of pythonPaths) {
        if (found) break;
        try {
          const testSpawn = spawn.sync(p, ['--version']);
          if (testSpawn.status === 0) {
            pythonPath = p;
            found = true;
            break;
          }
        } catch (e) {
          continue;
        }
      }

      if (!pythonPath) {
        const error = new Error('Python executable not found. Please install Python 3.8+');
        this.emit('error', error);
        reject(error);
        return;
      }

      console.log('🐍 Using Python:', pythonPath);

      // Check if notion.py exists, create if not
      const notionPyPath = path.join(__dirname, '../scripts/notion.py');
      if (!fs.existsSync(notionPyPath)) {
        console.warn('⚠️  notion.py not found, creating basic template...');
        this.createBasicNotionPy(notionPyPath, config);
      }

      // Spawn the Python process
      this.pythonProcess = spawn(pythonPath, [notionPyPath, ...args], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: path.dirname(notionPyPath),
        env: {
          ...process.env,
          NOTION_TOKEN: config.notionToken,
          MANUSCRIPT_VAULT: config.vaultPath,
          PYTHONPATH: path.join(__dirname, '../scripts'),
          DUAL_IDENTITY_ENABLED: config.generateManifest ? 'true' : 'false'
        }
      });
  
      this.isRunning = true;
      this.outputBuffer = [];
      this.errorBuffer = [];
      this.syncStartTime = Date.now();

      // Handle stdout
      this.pythonProcess.stdout.on('data', (data) => {
        const output = data.toString();
        this.outputBuffer.push(output);
        console.log('[Notion] STDOUT:', output.trim());
        this.emit('data', { type: 'stdout', data: output });
      });

      // Handle stderr
      this.pythonProcess.stderr.on('data', (data) => {
        const errorData = data.toString();
        this.errorBuffer.push(errorData);
        console.error('[Notion] STDERR:', errorData.trim());
        this.emit('error', { type: 'stderr', data: errorData });
      });

      // Handle process close
      this.pythonProcess.on('close', (code, signal) => {
        console.log(`🔄 Notion sync process exited with code ${code}${signal ? ` (signal: ${signal})` : ''}`);
        this.isRunning = false;
        
        const result = {
          status: code === 0 ? 'success' : 'error',
          exitCode: code,
          signal: signal,
          timestamp: new Date().toISOString(),
          output: this.outputBuffer.join(''),
          errors: this.errorBuffer.join(''),
          duration: Date.now() - this.syncStartTime,
          generateManifest: config.generateManifest
        };
  
        // Generate chonost.manifest.json if enabled and sync succeeded
        if (code === 0 && config.generateManifest) {
          console.log('📋 Generating chonost.manifest.json...');
          this.generateManifest(result)
            .then(manifestResult => {
              result.manifest = manifestResult;
              this.emit('complete', result);
              resolve(result);
            })
            .catch(manifestError => {
              console.error('⚠️  Manifest generation failed:', manifestError);
              result.manifestError = manifestError.message;
              this.emit('complete', result);
              resolve(result);
            });
        } else {
          this.emit('complete', result);
          if (code === 0) {
            resolve(result);
          } else {
            const error = new Error(`Notion sync failed with exit code ${code}`);
            error.result = result;
            reject(error);
          }
        }
      });

      // Handle process errors
      this.pythonProcess.on('error', (err) => {
        console.error('💥 Notion sync process error:', err);
        this.isRunning = false;
        this.emit('error', err);
        reject(err);
      });

      console.log('✅ Notion sync process started successfully');
      resolve({ status: 'started', pid: this.pythonProcess.pid });
    });
  }

  /**
   * Stop the Notion sync process
   * @returns {Promise} Process stop promise
   */
  async stopNotionSync() {
    return new Promise((resolve) => {
      if (!this.pythonProcess || !this.isRunning) {
        this.isRunning = false;
        resolve({ status: 'not_running' });
        return;
      }

      console.log('🛑 Stopping Notion sync process...');
      this.pythonProcess.kill('SIGTERM');

      // Force kill after 5 seconds if still running
      const timeout = setTimeout(() => {
        if (this.pythonProcess && !this.pythonProcess.killed) {
          console.log('⚡ Force killing Notion sync process...');
          this.pythonProcess.kill('SIGKILL');
        }
      }, 5000);

      this.pythonProcess.once('close', () => {
        clearTimeout(timeout);
        this.isRunning = false;
        this.pythonProcess = null;
        console.log('✅ Notion sync process stopped');
        resolve({ status: 'stopped' });
      });
    });
  }

  /**
   * Get current sync status
   * @returns {Object} Current status object
   */
  getStatus() {
    return {
      isRunning: this.isRunning,
      pid: this.pythonProcess?.pid || null,
      outputCount: this.outputBuffer.length,
      errorCount: this.errorBuffer.length,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Create basic notion.py template if it doesn't exist
   * @param {string} filePath - Path to create notion.py
   * @param {Object} config - Configuration options
   */
  createBasicNotionPy(filePath, config) {
    const basicNotionPy = `#!/usr/bin/env python3
"""
Basic Notion.py - Notion API integration for RAG pipeline
Syncs Notion data to manuscript vault
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Third-party imports (install with: pip install notion-client requests)
try:
    from notion_client import Client
    import requests
except ImportError as e:
    print(f"❌ Missing required packages: {e}")
    print("📦 Install with: pip install notion-client requests")
    sys.exit(1)

class NotionSync:
    def __init__(self, token=None, vault_path="./manuscript-vault"):
        self.notion = Client(auth=token or os.getenv('NOTION_TOKEN'))
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(exist_ok=True)
        self.sync_log = []
        
        print(f"📝 Notion Sync initialized")
        print(f"📁 Vault path: {self.vault_path.absolute()}")

    def sync_vault(self):
        """Sync Notion pages to manuscript vault"""
        try:
            # Example: Get database or pages from Notion
            # Replace with your actual Notion database ID
            database_id = os.getenv('NOTION_DATABASE_ID', 'your-database-id')
            
            print("🔍 Fetching Notion data...")
            results = self.notion.databases.query(
                database_id=database_id
            )
            
            sync_count = 0
            for page in results['results']:
                # Extract page content and metadata
                page_data = {
                    'id': page['id'],
                    'title': page['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Untitled'),
                    'created_time': page['created_time'],
                    'last_edited_time': page['last_edited_time'],
                    'url': page['url'],
                    'timestamp': datetime.now().isoformat()
                }
                
                # Save to vault as JSON
                vault_file = self.vault_path / f"notion_{page['id']}.json"
                with open(vault_file, 'w', encoding='utf-8') as f:
                    json.dump(page_data, f, indent=2, ensure_ascii=False)
                
                sync_count += 1
                self.sync_log.append(f"Synced: {page_data['title']}")
                print(f"✅ Synced page {sync_count}: {page_data['title']}")
            
            # Save sync log
            log_file = self.vault_path / "sync_log.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'sync_count': sync_count,
                    'timestamp': datetime.now().isoformat(),
                    'log': self.sync_log
                }, f, indent=2, ensure_ascii=False)
            
            print(f"🎉 Sync completed! {sync_count} items synced to vault.")
            return {'status': 'success', 'count': sync_count}
            
        except Exception as e:
            error_msg = f"❌ Sync failed: {str(e)}"
            print(error_msg)
            self.sync_log.append(error_msg)
            return {'status': 'error', 'message': str(e)}

def main():
    parser = argparse.ArgumentParser(description='Notion API integration for RAG pipeline')
    parser.add_argument('--sync-vault', action='store_true', help='Sync Notion data to manuscript vault')
    parser.add_argument('--token', help='Notion API token (overrides env var)')
    parser.add_argument('--vault', default='./manuscript-vault', help='Manuscript vault path')
    parser.add_argument('--database-id', help='Notion database ID')
    
    args = parser.parse_args()
    
    if args.token:
        os.environ['NOTION_TOKEN'] = args.token
    
    if args.database_id:
        os.environ['NOTION_DATABASE_ID'] = args.database_id
    
    print("🚀 Starting Notion sync...")
    print(f"📋 Arguments: {vars(args)}")
    
    sync = NotionSync(
        token=os.getenv('NOTION_TOKEN'),
        vault_path=args.vault
    )
    
    if args.sync_vault:
        result = sync.sync_vault()
        print(f"📊 Result: {json.dumps(result, indent=2)}")
        sys.exit(0 if result['status'] == 'success' else 1)
    else:
        print("ℹ️ No action specified. Use --sync-vault to sync data.")
        sys.exit(0)

if __name__ == '__main__':
    main()
`;

    try {
      fs.writeFileSync(filePath, basicNotionPy, 'utf8');
      console.log('✅ Created basic notion.py template');
      this.emit('file_created', { path: filePath });
    } catch (err) {
      console.error('❌ Failed to create notion.py:', err);
      this.emit('error', err);
    }
  }

  /**
   * Check if notion.py exists and is valid
   * @returns {Promise<boolean>} Validation result
   */
  async validateNotionPy() {
    const notionPyPath = path.join(__dirname, '../scripts/notion.py');
    
    if (!fs.existsSync(notionPyPath)) {
      console.log('⚠️  notion.py not found');
      return false;
    }
  
    try {
      // Basic syntax check
      const content = fs.readFileSync(notionPyPath, 'utf8');
      if (!content.includes('from notion_client import Client')) {
        console.log('⚠️  notion.py missing Notion client import');
        return false;
      }
      
      // Check for dual-identity support
      if (!content.includes('--generate-dual-identity')) {
        console.log('⚠️  notion.py missing dual-identity support');
        return false;
      }
      
      console.log('✅ notion.py validation passed (with dual-identity support)');
      return true;
    } catch (err) {
      console.error('❌ notion.py validation failed:', err);
      return false;
    }
  }
  
  /**
   * Generate chonost.manifest.json from sync results
   * @param {Object} syncResult - Result from notion.py sync
   * @returns {Promise<Object>} Manifest generation result
   */
  async generateManifest(syncResult) {
    return new Promise((resolve, reject) => {
      try {
        const { output, generateManifest } = syncResult;
        
        if (!generateManifest) {
          return resolve({ status: 'skipped', message: 'Manifest generation disabled' });
        }
  
        // Parse sync output for dual-identity data
        // This assumes notion.py returns JSON on stdout when --generate-dual-identity is used
        let syncData = [];
        try {
          // Extract JSON from output (notion.py will output structured data)
          const jsonMatch = output.match(/\{.*\}/s);
          if (jsonMatch) {
            syncData = JSON.parse(jsonMatch[0]);
          }
        } catch (parseError) {
          console.warn('⚠️  Could not parse sync data from output:', parseError.message);
          // Fallback: scan vault for .json files
          syncData = this.scanVaultForData();
        }
  
        // Generate dual-identity entries
        const manifestData = this.processDualIdentity(syncData);
  
        // Define manifest schema for validation
        const manifestSchema = {
          type: 'object',
          properties: {
            projects: { type: 'array', items: { type: 'object' } },
            files: { type: 'array', items: { type: 'object' } },
            diagrams: { type: 'array', items: { type: 'object' } },
            metadata: {
              type: 'object',
              properties: {
                version: { type: 'string', pattern: '^\\d+\\.\\d+\\.\\d+$' },
                lastSync: { type: 'string', format: 'date-time' },
                totalItems: { type: 'number' },
                dualIdentityEnabled: { type: 'boolean' }
              },
              required: ['version', 'lastSync', 'totalItems']
            }
          },
          required: ['metadata']
        };
  
        // Validate with AJV
        const Ajv = require('ajv');
        const ajv = new Ajv({ allErrors: true });
        const validate = ajv.compile(manifestSchema);
        
        const isValid = validate(manifestData);
        if (!isValid) {
          const error = new Error(`Manifest validation failed: ${JSON.stringify(validate.errors)}`);
          console.error('❌ Manifest validation errors:', validate.errors);
          return reject(error);
        }
  
        // Save manifest to file
        const manifestPath = path.join(__dirname, '../chonost.manifest.json');
        fs.writeFileSync(manifestPath, JSON.stringify(manifestData, null, 2), 'utf8');
        
        console.log(`✅ chonost.manifest.json generated: ${manifestPath}`);
        console.log(`📊 Items processed: ${manifestData.metadata.totalItems}`);
        
        // Emit manifest event
        this.emit('manifest_generated', {
          path: manifestPath,
          items: manifestData.metadata.totalItems,
          timestamp: new Date().toISOString()
        });
  
        resolve({
          status: 'success',
          path: manifestPath,
          items: manifestData.metadata.totalItems,
          valid: true
        });
  
      } catch (error) {
        console.error('💥 Manifest generation error:', error);
        reject(error);
      }
    });
  }
  
  /**
   * Scan vault directory for existing data files
   * @returns {Array} Array of vault data objects
   */
  scanVaultForData() {
    const vaultPath = process.env.MANUSCRIPT_VAULT || './manuscript-vault';
    const vaultDir = path.join(__dirname, '../', vaultPath);
    
    if (!fs.existsSync(vaultDir)) {
      console.warn('⚠️  Vault directory not found:', vaultDir);
      return [];
    }
  
    const data = [];
    try {
      const files = fs.readdirSync(vaultDir).filter(f => f.endsWith('.json'));
      
      files.forEach(filename => {
        try {
          const filePath = path.join(vaultDir, filename);
          const content = fs.readFileSync(filePath, 'utf8');
          const jsonData = JSON.parse(content);
          
          data.push({
            id: filename.replace('.json', ''),
            title: jsonData.title || 'Untitled',
            type: this.inferFileType(filename, jsonData),
            thaiName: '', // Will be generated
            englishName: jsonData.title || 'Untitled',
            path: filePath,
            timestamp: jsonData.timestamp || new Date().toISOString()
          });
        } catch (fileError) {
          console.warn(`⚠️  Skipping invalid file ${filename}:`, fileError.message);
        }
      });
      
    } catch (dirError) {
      console.error('❌ Error scanning vault:', dirError);
    }
    
    return data;
  }
  
  /**
   * Process dual-identity naming for vault items
   * @param {Array} items - Array of vault data objects
   * @returns {Object} Processed manifest data
   */
  processDualIdentity(items) {
    const { translate } = require('google-translate-api');
    const projects = [];
    const files = [];
    const diagrams = [];
    
    items.forEach(item => {
      const entry = {
        id: item.id,
        thaiName: item.thaiName || this.generateThaiName(item.title),
        englishName: item.englishName || item.title,
        localPath: item.path,
        cloudId: item.id,
        tags: item.tags || this.extractTags(item),
        type: item.type,
        created: item.created_time || item.timestamp,
        updated: item.last_edited_time || item.timestamp,
        url: item.url
      };
      
      // Basic type classification
      if (item.type === 'project' || entry.thaiName.includes('โปรเจกต์')) {
        projects.push(entry);
      } else if (entry.thaiName.includes('แผนภาพ') || entry.thaiName.includes('diagram')) {
        diagrams.push(entry);
      } else {
        files.push(entry);
      }
    });
    
    return {
      projects,
      files,
      diagrams,
      metadata: {
        version: '1.0.0',
        lastSync: new Date().toISOString(),
        totalItems: items.length,
        dualIdentityEnabled: true,
        projectsCount: projects.length,
        filesCount: files.length,
        diagramsCount: diagrams.length
      }
    };
  }
  
  /**
   * Generate Thai name from English (placeholder - integrate with real translation)
   * @param {string} englishName - English name
   * @returns {string} Generated Thai name
   */
  generateThaiName(englishName) {
    // Simple mapping for common terms (expand as needed)
    const thaiMap = {
      'project': 'โปรเจกต์',
      'report': 'รายงาน',
      'document': 'เอกสาร',
      'diagram': 'แผนภาพ',
      'notes': 'บันทึก',
      'analysis': 'การวิเคราะห์',
      'draft': 'ร่าง'
    };
    
    let thaiName = englishName;
    
    // Basic keyword replacement
    Object.keys(thaiMap).forEach(english => {
      const regex = new RegExp(`\\b${english}\\b`, 'gi');
      thaiName = thaiName.replace(regex, thaiMap[english]);
    });
    
    // For unknown terms, use placeholder translation
    if (thaiName === englishName) {
      console.log(`ℹ️  Using placeholder translation for: ${englishName}`);
      thaiName = `เอกสาร: ${englishName}`; // Generic Thai prefix
    }
    
    return thaiName;
  }
  
  /**
   * Extract tags from item content (placeholder implementation)
   * @param {Object} item - Item data
   * @returns {Array} Extracted tags
   */
  extractTags(item) {
    // Simple keyword-based tagging (expand with ML model later)
    const content = (item.properties || {}).rich_text?.[0]?.plain_text || item.title || '';
    const keywords = content.toLowerCase().match(/\b\w{4,}\b/g) || [];
    
    const tagMap = {
      'project': 'project',
      'report': 'report',
      'analysis': 'analysis',
      'diagram': 'visual',
      'draft': 'wip',
      'final': 'complete'
    };
    
    const tags = new Set();
    keywords.forEach(word => {
      const cleanWord = word.replace(/[^\w]/g, '');
      if (tagMap[cleanWord]) {
        tags.add(tagMap[cleanWord]);
      }
    });
    
    // Add type-based tags
    if (item.type) {
      tags.add(item.type);
    }
    
    return Array.from(tags);
  }
  
  /**
   * Infer file type from filename and content
   * @param {string} filename - File name
   * @param {Object} data - File data
   * @returns {string} Inferred type
   */
  inferFileType(filename, data) {
    const ext = path.extname(filename).toLowerCase();
    const name = path.basename(filename, ext).toLowerCase();
    
    if (ext === '.md' && (name.includes('project') || name.includes('โปรเจกต์'))) {
      return 'project';
    }
    
    if (['.png', '.jpg', '.svg'].includes(ext) || name.includes('diagram') || name.includes('แผนภาพ')) {
      return 'diagram';
    }
    
    if (data.properties?.diagram || data.content?.includes('```mermaid') || data.content?.includes('```plantuml')) {
      return 'diagram';
    }
    
    return 'file';
  }
}

// Create and export sidecar instance
const notionSidecar = new NotionSidecar();

// API for Tauri integration
module.exports = {
  start: (options) => notionSidecar.startNotionSync(options),
  stop: () => notionSidecar.stopNotionSync(),
  status: () => notionSidecar.getStatus(),
  validate: () => notionSidecar.validateNotionPy(),
  on: (event, listener) => notionSidecar.on(event, listener),
  emit: (event, data) => notionSidecar.emit(event, data)
};

// Example usage for direct Node.js execution
if (require.main === module) {
  console.log('🛠️  Nodition Sidecar starting...');
  
  // Listen for events
  notionSidecar.on('data', (data) => {
    console.log(`📨 Event: ${data.type}`, data.data);
  });
  
  notionSidecar.on('error', (err) => {
    console.error('💥 Sidecar error:', err);
  });
  
  notionSidecar.on('complete', (result) => {
    console.log('🏁 Sync completed:', result.status);
  });
  
  // Start sync if sync-vault flag is provided
  const args = process.argv.slice(2);
  if (args.includes('--sync-vault')) {
    notionSidecar.startNotionSync({ syncVault: true })
      .then((result) => {
        console.log('🎉 Sync initiated:', result);
        process.exit(0);
      })
      .catch((err) => {
        console.error('💥 Sync failed:', err);
        process.exit(1);
      });
  } else {
    console.log('ℹ️  Use --sync-vault to start Notion sync');
    console.log('📊 Current status:', notionSidecar.getStatus());
  }
}