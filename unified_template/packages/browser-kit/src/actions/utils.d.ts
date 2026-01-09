import type { Browser } from 'puppeteer-core';
import type { BrowserConfig } from '../config.js';
export declare function withBrowser<T>(action: (browser: Browser) => Promise<T>, config?: BrowserConfig): Promise<T>;
//# sourceMappingURL=utils.d.ts.map