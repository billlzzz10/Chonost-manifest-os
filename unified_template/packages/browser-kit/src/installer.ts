import { join } from 'node:path';
import { mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { BrowserConfig, resolveConfig } from './config.js';
import { install, Browser } from '@puppeteer/browsers';

const DEFAULT_CHANNEL: Browser = Browser.CHROME

export async function ensureBrowserInstalled(config: BrowserConfig): Promise<string> {
  const resolved = resolveConfig(config);
  if (resolved.executablePath && existsSync(resolved.executablePath)) {
    return resolved.executablePath;
  }

  const cacheDir = resolved.cacheDir;
  await mkdir(cacheDir, { recursive: true });
  const installResult = await install({
    cacheDir,
    browser: DEFAULT_CHANNEL,
    buildId: 'stable'
  });

  return join(installResult.path, installResult.executablePath);
}

