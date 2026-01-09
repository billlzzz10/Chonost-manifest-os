import { launchBrowser } from '../launcher.js';
export async function withBrowser(action, config = {}) {
    const browser = await launchBrowser(config);
    try {
        return await action(browser);
    }
    finally {
        await browser.close();
    }
}
//# sourceMappingURL=utils.js.map