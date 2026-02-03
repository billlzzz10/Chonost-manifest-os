import { ensureBrowserInstalled } from './installer.js';
import { resolveConfig } from './config.js';
import puppeteer from 'puppeteer-core';
export async function launchBrowser(overrides = {}) {
    const config = resolveConfig(overrides);
    const executablePath = await ensureBrowserInstalled(config);
    return puppeteer.launch({
        executablePath,
        headless: config.headless,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
}
//# sourceMappingURL=launcher.js.map