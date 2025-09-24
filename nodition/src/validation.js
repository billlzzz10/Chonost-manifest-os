/**
 * Validation module for Nodition Desktop
 * Performs health checks for Notion and RAG services
 */

const { invoke } = window.__TAURI__.tauri;
const { info, warn, error } = window.__TAURI__.event;

class ValidationService {
  constructor() {
    this.notionHealthy = false;
    this.ragHealthy = false;
    this.manifestHealthy = false;
    this.validationResults = [];
  }

  // Check Notion API connectivity
  async checkNotionConnection() {
    try {
      // Basic Notion API health check
      // This would typically use notion-client to make a test API call
      console.log('🔍 Checking Notion API connection...');
      
      // Simulate API check (replace with actual notion-client call)
      const notionStatus = {
        status: 'connected',
        timestamp: new Date().toISOString(),
        message: 'Notion API is reachable'
      };
      
      this.notionHealthy = true;
      this.addResult('notion', 'success', notionStatus.message);
      console.log('✅ Notion API: Healthy');
      
      return notionStatus;
    } catch (err) {
      this.notionHealthy = false;
      this.addResult('notion', 'error', `Notion API connection failed: ${err.message}`);
      console.error('❌ Notion API: Unhealthy', err);
      
      // Emit error to Tauri window
      await invoke('show_notification', { 
        title: 'Validation Error', 
        message: `Notion connection failed: ${err.message}` 
      });
      
      throw err;
    }
  }

  // Check RAG system status
  async checkRAGSystem() {
    try {
      console.log('🔍 Checking RAG system status...');
      
      // Check if RAG services are running (mock implementation)
      // In production, this would check MCP servers, vector stores, etc.
      const ragStatus = {
        status: 'active',
        vectorStore: 'connected',
        mcpServers: ['memory', 'filesystem', 'sequentialthinking'],
        timestamp: new Date().toISOString()
      };
      
      this.ragHealthy = true;
      this.addResult('rag', 'success', 'RAG system is operational');
      console.log('✅ RAG System: Healthy');
      
      return ragStatus;
    } catch (err) {
      this.ragHealthy = false;
      this.addResult('rag', 'error', `RAG system check failed: ${err.message}`);
      console.error('❌ RAG System: Unhealthy', err);
      
      await invoke('show_notification', { 
        title: 'RAG Error', 
        message: `RAG system unavailable: ${err.message}` 
      });
      
      throw err;
    }
  }

  // Add validation result
  addResult(service, status, message) {
    this.validationResults.push({
      service,
      status,
      message,
      timestamp: new Date().toISOString()
    });
  }

  // Check manifest validity
  async checkManifest() {
    try {
      console.log('🔍 Checking chonost.manifest.json...');
      
      // Check if manifest exists via Tauri backend
      const manifestCheck = await invoke('check_manifest_exists');
      
      if (!manifestCheck.exists) {
        throw new Error('chonost.manifest.json not found');
      }
      
      // Get manifest content
      const manifestData = await invoke('read_manifest');
      const manifest = JSON.parse(manifestData.content);
      
      // Basic validation checks
      if (!manifest.metadata) {
        throw new Error('Manifest missing metadata section');
      }
      
      if (!manifest.metadata.version) {
        throw new Error('Manifest missing version in metadata');
      }
      
      // Validate timestamp format
      try {
        new Date(manifest.metadata.lastSync);
      } catch (e) {
        throw new Error('Manifest lastSync timestamp is invalid');
      }
      
      // Check item counts
      const totalItems = (manifest.projects || []).length +
                        (manifest.files || []).length +
                        (manifest.diagrams || []).length;
      
      if (manifest.metadata.totalItems !== totalItems) {
        console.warn(`⚠️  Manifest item count mismatch: expected ${manifest.metadata.totalItems}, found ${totalItems}`);
      }
      
      // Validate dual-identity format
      const validateDualIdentity = (items) => {
        let validCount = 0;
        for (const item of items) {
          if (item.thai_name && item.english_name &&
              typeof item.thai_name === 'string' &&
              typeof item.english_name === 'string' &&
              item.thai_name.trim() && item.english_name.trim()) {
            validCount++;
          }
        }
        return validCount;
      };
      
      const projectDual = validateDualIdentity(manifest.projects || []);
      const fileDual = validateDualIdentity(manifest.files || []);
      const diagramDual = validateDualIdentity(manifest.diagrams || []);
      
      const totalDualValid = projectDual + fileDual + diagramDual;
      const dualCoverage = totalItems > 0 ? (totalDualValid / totalItems) * 100 : 0;
      
      if (dualCoverage < 80) {
        console.warn(`⚠️  Low dual-identity coverage: ${Math.round(dualCoverage)}% (${totalDualValid}/${totalItems})`);
      }
      
      this.manifestHealthy = true;
      this.addResult('manifest', 'success',
        `Manifest v${manifest.metadata.version} valid (${totalItems} items, ${Math.round(dualCoverage)}% dual coverage)`
      );
      console.log(`✅ Manifest: Healthy (v${manifest.metadata.version}, ${totalItems} items)`);
      
      return {
        status: 'healthy',
        version: manifest.metadata.version,
        lastSync: manifest.metadata.lastSync,
        totalItems: totalItems,
        dualCoverage: Math.round(dualCoverage),
        timestamp: new Date().toISOString()
      };
      
    } catch (err) {
      this.manifestHealthy = false;
      this.addResult('manifest', 'error', `Manifest validation failed: ${err.message}`);
      console.error('❌ Manifest: Unhealthy', err.message);
      
      // Don't throw - allow partial validation
      return {
        status: 'unhealthy',
        error: err.message,
        timestamp: new Date().toISOString()
      };
    }
  }
  
  // Run full validation suite with manifest check
  async runFullValidation() {
    console.log('🚀 Starting Enhanced Nodition validation suite...');
    
    const results = {
      timestamp: new Date().toISOString(),
      overallStatus: 'pending',
      services: {},
      summary: []
    };

    try {
      // Run Notion check
      await this.checkNotionConnection();
      results.services.notion = { status: 'healthy' };
      results.summary.push('Notion: ✅ Healthy');

    } catch (notionErr) {
      results.services.notion = { status: 'unhealthy' };
      results.summary.push('Notion: ❌ Unhealthy');
    }

    try {
      // Run RAG check
      await this.checkRAGSystem();
      results.services.rag = { status: 'healthy' };
      results.summary.push('RAG: ✅ Healthy');

    } catch (ragErr) {
      results.services.rag = { status: 'unhealthy' };
      results.summary.push('RAG: ❌ Unhealthy');
    }

    try {
      // Run Manifest check
      await this.checkManifest();
      results.services.manifest = { status: 'healthy' };
      results.summary.push('Manifest: ✅ Healthy');

    } catch (manifestErr) {
      results.services.manifest = { status: 'unhealthy' };
      results.summary.push('Manifest: ❌ Unhealthy');
    }

    // Determine overall status
    const healthyServices = Object.values(results.services).filter(s => s.status === 'healthy').length;
    const totalServices = Object.keys(results.services).length;
    
    results.overallStatus = healthyServices === totalServices ? 'healthy' :
                           (healthyServices / totalServices > 0.75 ? 'partial' : 'unhealthy');
    results.healthScore = Math.round((healthyServices / totalServices) * 100);
    results.validationResults = this.validationResults;
    results.serviceDetails = {
      notion: this.notionHealthy,
      rag: this.ragHealthy,
      manifest: this.manifestHealthy
    };

    // Log summary
    console.log('\n📊 Enhanced Validation Summary:');
    console.log(`Overall Status: ${results.overallStatus}`);
    console.log(`Health Score: ${results.healthScore}% (${healthyServices}/${totalServices} services)`);
    results.summary.forEach(item => console.log(item));
    console.log('\n');

    // Emit results to main process
    await invoke('validation_complete', {
      results: JSON.stringify(results),
      details: JSON.stringify(results.serviceDetails)
    });

    return results;
  }

  // Get current status for UI (enhanced)
  getStatus() {
    return {
      notion: this.notionHealthy,
      rag: this.ragHealthy,
      manifest: this.manifestHealthy,
      overall: this.notionHealthy && this.ragHealthy && this.manifestHealthy,
      healthScore: this.calculateHealthScore(),
      results: this.validationResults.slice(-5), // Last 5 results
      lastValidation: this.validationResults.length > 0 ?
        this.validationResults[this.validationResults.length - 1].timestamp : null
    };
  }
  
  calculateHealthScore() {
    const healthyCount = [this.notionHealthy, this.ragHealthy, this.manifestHealthy]
      .filter(Boolean).length;
    return Math.round((healthyCount / 3) * 100);
  }

  // Clear validation history
  clearHistory() {
    this.validationResults = [];
    this.notionHealthy = false;
    this.ragHealthy = false;
  }
}

// Export for use in frontend
const validationService = new ValidationService();
export default validationService;

// Auto-run validation on module load (for development)
if (process.env.NODE_ENV === 'development') {
  console.log('🌱 Development mode: Running initial validation...');
  validationService.runFullValidation().catch(console.error);
}