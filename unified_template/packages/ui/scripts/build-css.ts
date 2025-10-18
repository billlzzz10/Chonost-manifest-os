import { writeFile } from "node:fs/promises";

const css = `:root {
  --ui-font-sans: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --ui-radius-sm: 6px;
  --ui-radius-md: 12px;
  --ui-surface: #111418;
  --ui-surface-alt: #1b1f24;
  --ui-border: #262c35;
  --ui-text: #f5f7fb;
  --ui-text-muted: #a0a8b8;
  --ui-accent: #62d1ff;
}

[data-theme="light"] {
  --ui-surface: #ffffff;
  --ui-surface-alt: #f5f7fb;
  --ui-border: #d9dfea;
  --ui-text: #1a1c23;
  --ui-text-muted: #4c566a;
  --ui-accent: #2563eb;
}
`;

await writeFile(new URL("../styles.css", import.meta.url), css, "utf8");
