import { describe, expect, it } from 'vitest';
import { resolveConfig } from '../src/config.js';

describe('browser-kit config', () => {
  it('falls back to defaults', () => {
    const config = resolveConfig();
    expect(config.cacheDir.length).toBeGreaterThan(0);
    expect(config.headless).toBe(true);
  });
});

