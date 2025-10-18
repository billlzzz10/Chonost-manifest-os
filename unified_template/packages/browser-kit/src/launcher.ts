import { ensureBrowserInstalled } from './installer.js';
import { resolveConfig, type BrowserConfig } from './config.js';
import type { Browser } from 'puppeteer-core';
import puppeteer from 'puppeteer-core';

export interface LaunchOptions extends BrowserConfig {}

export async function launchBrowser(overrides: LaunchOptions = {}): Promise<Browser> {
  const config = resolveConfig(overrides);
  const executablePath = await ensureBrowserInstalled(config);
  return puppeteer.launch({
    executablePath,
    headless: config.headless,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
}

