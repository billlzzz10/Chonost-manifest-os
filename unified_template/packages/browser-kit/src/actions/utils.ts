import type { Browser } from 'puppeteer-core';
import type { BrowserConfig } from '../config.js';
import { launchBrowser } from '../launcher.js';

export async function withBrowser<T>(
  action: (browser: Browser) => Promise<T>,
  config: BrowserConfig = {}
): Promise<T> {
  const browser = await launchBrowser(config);
  try {
    return await action(browser);
  } finally {
    await browser.close();
  }
}

