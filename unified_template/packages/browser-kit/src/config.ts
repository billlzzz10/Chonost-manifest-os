const DEFAULT_CACHE = process.env.BROWSER_CACHE_PATH ?? '.runtime/browser-cache';

export interface BrowserConfig {
  cacheDir?: string;
  headless?: boolean;
  executablePath?: string;
}

export function resolveConfig(overrides: BrowserConfig = {}): Required<BrowserConfig> {
  return {
    cacheDir: overrides.cacheDir ?? DEFAULT_CACHE,
    headless: overrides.headless ?? true,
    executablePath: overrides.executablePath ?? process.env.PUPPETEER_EXECUTABLE_PATH ?? ''
  };
}

