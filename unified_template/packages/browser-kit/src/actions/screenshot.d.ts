import type { BrowserConfig } from '../config.js';
export interface ScreenshotOptions extends BrowserConfig {
    fullPage?: boolean;
    outputPath: string;
}
export declare function captureScreenshot(url: string, options: ScreenshotOptions): Promise<string>;
//# sourceMappingURL=screenshot.d.ts.map