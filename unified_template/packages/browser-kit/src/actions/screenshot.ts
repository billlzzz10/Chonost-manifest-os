import { withBrowser } from './utils.js';
import type { BrowserConfig } from '../config.js';

export interface ScreenshotOptions extends BrowserConfig {
  fullPage?: boolean;
  outputPath: string;
}

export async function captureScreenshot(url: string, options: ScreenshotOptions): Promise<string> {
  const { outputPath, fullPage, ...browserConfig } = options;
  await withBrowser(async (browser) => {
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle2' });
    await page.screenshot({ path: outputPath, fullPage: fullPage ?? false });
    await page.close();
  }, browserConfig);

  return outputPath;
}

