import { withBrowser } from './utils.js';
import type { BrowserConfig } from '../config.js';

export async function extractHtml(url: string, config: BrowserConfig = {}): Promise<string> {
  return withBrowser(async (browser) => {
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    const content = await page.content();
    await page.close();
    return content;
  }, config);
}

