import { type BrowserConfig } from './config.js';
import type { Browser } from 'puppeteer-core';
export interface LaunchOptions extends BrowserConfig {
}
export declare function launchBrowser(overrides?: LaunchOptions): Promise<Browser>;
//# sourceMappingURL=launcher.d.ts.map