'use strict';

const assert = require('node:assert/strict');
const fs = require('fs/promises');
const os = require('os');
const path = require('path');
const { test } = require('node:test');

const CONFIG_FILENAME = 'mcp.json';

test('loadConfig refreshes cache when configuration changes', async (t) => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'mcp-toolbox-'));
  const originalRoot = process.env.MCP_PROJECT_ROOT;
  process.env.MCP_PROJECT_ROOT = tempDir;

  t.after(async () => {
    process.env.MCP_PROJECT_ROOT = originalRoot;
    await fs.rm(tempDir, { recursive: true, force: true });
    delete require.cache[require.resolve('./index')];
  });

  delete require.cache[require.resolve('./index')];
  const { loadMCPConfig } = require('./index');

  const defaultConfig = await loadMCPConfig();
  assert.deepStrictEqual(defaultConfig, { servers: {}, inputs: [] });

  const configPath = path.join(tempDir, CONFIG_FILENAME);
  const firstConfig = {
    servers: { alpha: { type: 'http', url: 'https://one.example' } },
    inputs: []
  };
  await fs.writeFile(configPath, JSON.stringify(firstConfig), 'utf8');

  const initialLoad = await loadMCPConfig();
  assert.deepStrictEqual(initialLoad, firstConfig);

  await new Promise((resolve) => setTimeout(resolve, 50));

  const secondConfig = {
    servers: { beta: { type: 'http', url: 'https://two.example' } },
    inputs: [{ name: 'beta' }]
  };
  await fs.writeFile(configPath, JSON.stringify(secondConfig), 'utf8');

  const refreshedLoad = await loadMCPConfig();
  assert.deepStrictEqual(refreshedLoad, secondConfig);

  await fs.rm(configPath);

  const fallbackLoad = await loadMCPConfig();
  assert.deepStrictEqual(fallbackLoad, { servers: {}, inputs: [] });
});
