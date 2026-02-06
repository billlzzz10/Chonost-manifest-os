const DEFAULT_CACHE = process.env.BROWSER_CACHE_PATH ?? '.runtime/browser-cache';
export function resolveConfig(overrides = {}) {
    return {
        cacheDir: overrides.cacheDir ?? DEFAULT_CACHE,
        headless: overrides.headless ?? true,
        executablePath: overrides.executablePath ?? process.env.PUPPETEER_EXECUTABLE_PATH ?? ''
    };
}
//# sourceMappingURL=config.js.map