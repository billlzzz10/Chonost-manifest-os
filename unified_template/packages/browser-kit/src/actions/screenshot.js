import { withBrowser } from './utils.js';
export async function captureScreenshot(url, options) {
    const { outputPath, fullPage, ...browserConfig } = options;
    await withBrowser(async (browser) => {
        const page = await browser.newPage();
        await page.goto(url, { waitUntil: 'networkidle2' });
        await page.screenshot({ path: outputPath, fullPage: fullPage ?? false });
        await page.close();
    }, browserConfig);
    return outputPath;
}
//# sourceMappingURL=screenshot.js.map