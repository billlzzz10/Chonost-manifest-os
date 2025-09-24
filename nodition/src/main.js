// src/main.js - Main entry point for Nodition frontend
import validationService from './validation.js';

console.log('🚀 Nodition frontend loaded');

// Basic app initialization
document.addEventListener('DOMContentLoaded', async () => {
  console.log('📱 DOM loaded, initializing Nodition app');
  
  try {
    // Run initial validation
    const results = await validationService.runFullValidation();
    console.log('✅ Initial validation completed:', results.overallStatus);
    
    // Setup event listeners
    setupEventListeners();
    
  } catch (error) {
    console.error('❌ App initialization failed:', error);
    document.getElementById('status-text').textContent = `Initialization Error: ${error.message}`;
  }
});

function setupEventListeners() {
  const validateBtn = document.getElementById('validate-btn');
  const syncBtn = document.getElementById('sync-btn');
  const stopBtn = document.getElementById('stop-btn');
  
  if (validateBtn) {
    validateBtn.addEventListener('click', async () => {
      validateBtn.disabled = true;
      validateBtn.textContent = 'Validating...';
      
      try {
        const results = await validationService.runFullValidation();
        updateStatusDisplay(results);
        console.log('Validation triggered by user');
      } catch (error) {
        console.error('Validation error:', error);
      } finally {
        validateBtn.disabled = false;
        validateBtn.textContent = 'Run Validation';
      }
    });
  }
  
  if (syncBtn) {
    syncBtn.addEventListener('click', async () => {
      console.log('Notion sync requested');
      // Sidecar integration will be handled by inline script in index.html
      alert('Notion sync functionality will be implemented with sidecar integration');
    });
  }
  
  console.log('Event listeners attached');
}

function updateStatusDisplay(results) {
  const statusEl = document.getElementById('status');
  const statusTextEl = document.getElementById('status-text');
  const healthScoreEl = document.getElementById('health-score');
  
  if (results.overallStatus === 'healthy') {
    statusEl.className = 'status healthy';
    statusTextEl.textContent = '🟢 All systems healthy';
  } else {
    statusEl.className = 'status error';
    statusTextEl.textContent = `🟡 Health: ${results.healthScore}%`;
  }
  
  healthScoreEl.textContent = `Health Score: ${results.healthScore}%`;
}

// Export for potential module usage
export default {
  init: () => {
    console.log('Nodition app module initialized');
    return validationService;
  },
  validate: () => validationService.runFullValidation(),
  status: () => validationService.getStatus()
};