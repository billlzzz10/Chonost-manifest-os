import { withBrowser } from './utils.js';
export async function extractHtml(url, config = {}) {
    return withBrowser(async (browser) => {
        const page = await browser.newPage();
        await page.goto(url, { waitUntil: 'domcontentloaded' });
        const content = await page.content();
        await page.close();
        return content;
    }, config);
}
//# sourceMappingURL=html.js.map