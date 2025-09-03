// src/plugins/linter.ts
// Linter Plugin - Provides writing assistance and content analysis
// Similar to Grammarly but focused on technical writing and markdown

import type { Plugin, PluginContext } from "./index";

interface LintRule {
  id: string;
  name: string;
  description: string;
  category: "grammar" | "style" | "structure" | "markdown" | "technical";
  severity: "error" | "warning" | "info";
  check: (text: string) => LintIssue[];
}

interface LintIssue {
  ruleId: string;
  message: string;
  line: number;
  column: number;
  length: number;
  severity: "error" | "warning" | "info";
  suggestions?: string[];
}

class ContentLinter {
  private rules: Map<string, LintRule> = new Map();
  private context: PluginContext;
  private enabled: boolean = true;

  constructor(context: PluginContext) {
    this.context = context;
    this.initializeRules();
  }

  private initializeRules() {
    const rules: LintRule[] = [
      // Grammar Rules
      {
        id: "double-spaces",
        name: "Double Spaces",
        description: "Detect multiple consecutive spaces",
        category: "grammar",
        severity: "warning",
        check: (text: string) => {
          const issues: LintIssue[] = [];
          const lines = text.split("\n");

          lines.forEach((line, lineIndex) => {
            const matches = line.matchAll(/  +/g);
            for (const match of matches) {
              issues.push({
                ruleId: "double-spaces",
                message: "Multiple consecutive spaces found",
                line: lineIndex + 1,
                column: match.index! + 1,
                length: match[0].length,
                severity: "warning",
                suggestions: [" "],
              });
            }
          });

          return issues;
        },
      },

      // Markdown Rules
      {
        id: "missing-alt-text",
        name: "Missing Alt Text",
        description: "Images should have alt text for accessibility",
        category: "markdown",
        severity: "warning",
        check: (text: string) => {
          const issues: LintIssue[] = [];
          const lines = text.split("\n");

          lines.forEach((line, lineIndex) => {
            const matches = line.matchAll(/!\[\s*\]\([^)]+\)/g);
            for (const match of matches) {
              issues.push({
                ruleId: "missing-alt-text",
                message: "Image is missing alt text",
                line: lineIndex + 1,
                column: match.index! + 1,
                length: match[0].length,
                severity: "warning",
                suggestions: ["Add descriptive alt text between the brackets"],
              });
            }
          });

          return issues;
        },
      },

      // Style Rules
      {
        id: "long-sentences",
        name: "Long Sentences",
        description: "Sentences should be concise and readable",
        category: "style",
        severity: "info",
        check: (text: string) => {
          const issues: LintIssue[] = [];
          const lines = text.split("\n");

          lines.forEach((line, lineIndex) => {
            const sentences = line.split(/[.!?]+/);
            let columnOffset = 0;

            sentences.forEach((sentence) => {
              const trimmed = sentence.trim();
              if (trimmed.length > 100) {
                issues.push({
                  ruleId: "long-sentences",
                  message: `Sentence is ${trimmed.length} characters long. Consider breaking it up.`,
                  line: lineIndex + 1,
                  column: columnOffset + 1,
                  length: trimmed.length,
                  severity: "info",
                  suggestions: [
                    "Consider breaking this sentence into smaller parts",
                  ],
                });
              }
              columnOffset += sentence.length + 1;
            });
          });

          return issues;
        },
      },

      // Structure Rules
      {
        id: "heading-hierarchy",
        name: "Heading Hierarchy",
        description: "Headings should follow proper hierarchy (H1 -> H2 -> H3)",
        category: "structure",
        severity: "warning",
        check: (text: string) => {
          const issues: LintIssue[] = [];
          const lines = text.split("\n");
          let lastHeadingLevel = 0;

          lines.forEach((line, lineIndex) => {
            const headingMatch = line.match(/^(#{1,6})\s/);
            if (headingMatch) {
              const currentLevel = headingMatch[1].length;

              if (currentLevel > lastHeadingLevel + 1) {
                issues.push({
                  ruleId: "heading-hierarchy",
                  message: `Heading level ${currentLevel} follows level ${lastHeadingLevel}. Consider using level ${
                    lastHeadingLevel + 1
                  } instead.`,
                  line: lineIndex + 1,
                  column: 1,
                  length: headingMatch[0].length,
                  severity: "warning",
                  suggestions: [
                    `Use ${"#".repeat(lastHeadingLevel + 1)} instead`,
                  ],
                });
              }

              lastHeadingLevel = currentLevel;
            }
          });

          return issues;
        },
      },

      // Technical Writing Rules
      {
        id: "passive-voice",
        name: "Passive Voice",
        description: "Prefer active voice for clearer writing",
        category: "technical",
        severity: "info",
        check: (text: string) => {
          const issues: LintIssue[] = [];
          const lines = text.split("\n");

          // Simple passive voice detection (can be improved)
          const passivePatterns = [
            /\b(is|are|was|were|being|been)\s+\w+ed\b/gi,
            /\b(is|are|was|were)\s+\w+en\b/gi,
          ];

          lines.forEach((line, lineIndex) => {
            passivePatterns.forEach((pattern) => {
              const matches = line.matchAll(pattern);
              for (const match of matches) {
                issues.push({
                  ruleId: "passive-voice",
                  message: "Consider using active voice for clearer writing",
                  line: lineIndex + 1,
                  column: match.index! + 1,
                  length: match[0].length,
                  severity: "info",
                  suggestions: ["Rewrite in active voice"],
                });
              }
            });
          });

          return issues;
        },
      },

      // Code Block Rules
      {
        id: "unlabeled-code-blocks",
        name: "Unlabeled Code Blocks",
        description: "Code blocks should specify the programming language",
        category: "markdown",
        severity: "info",
        check: (text: string) => {
          const issues: LintIssue[] = [];
          const lines = text.split("\n");

          lines.forEach((line, lineIndex) => {
            if (line.trim() === "```") {
              issues.push({
                ruleId: "unlabeled-code-blocks",
                message: "Code block should specify the programming language",
                line: lineIndex + 1,
                column: 1,
                length: 3,
                severity: "info",
                suggestions: [
                  "Add language identifier: ```javascript, ```python, etc.",
                ],
              });
            }
          });

          return issues;
        },
      },
    ];

    rules.forEach((rule) => {
      this.rules.set(rule.id, rule);
    });
  }

  lintContent(content: string): LintIssue[] {
    if (!this.enabled) return [];

    const allIssues: LintIssue[] = [];

    for (const rule of this.rules.values()) {
      try {
        const issues = rule.check(content);
        allIssues.push(...issues);
      } catch (error) {
        console.error(`Error in lint rule ${rule.id}:`, error);
      }
    }

    return allIssues.sort((a, b) => {
      if (a.line !== b.line) return a.line - b.line;
      return a.column - b.column;
    });
  }

  getIssuesByCategory(issues: LintIssue[]): Record<string, LintIssue[]> {
    const byCategory: Record<string, LintIssue[]> = {};

    for (const issue of issues) {
      const rule = this.rules.get(issue.ruleId);
      if (rule) {
        if (!byCategory[rule.category]) {
          byCategory[rule.category] = [];
        }
        byCategory[rule.category].push(issue);
      }
    }

    return byCategory;
  }

  getIssueCounts(issues: LintIssue[]): Record<string, number> {
    const counts = { error: 0, warning: 0, info: 0 };

    for (const issue of issues) {
      counts[issue.severity]++;
    }

    return counts;
  }

  toggleRule(ruleId: string, enabled: boolean): void {
    const rule = this.rules.get(ruleId);
    if (rule) {
      // In a real implementation, we'd store this in settings
      console.log(`Rule ${ruleId} ${enabled ? "enabled" : "disabled"}`);
    }
  }

  setEnabled(enabled: boolean): void {
    this.enabled = enabled;
  }

  isEnabled(): boolean {
    return this.enabled;
  }

  getRules(): LintRule[] {
    return Array.from(this.rules.values());
  }
}

export const linterPlugin: Plugin = {
  id: "linter",
  name: "Content Linter",
  version: "1.0.0",
  description: "Provides writing assistance and content analysis",
  author: "Craft IDE Team",

  onLoad: async (context: PluginContext) => {
    const linter = new ContentLinter(context);

    // Store linter instance for command access
    (globalThis as any).__craftLinter = linter;
  },

  commands: [
    {
      id: "lint-content",
      name: "Lint Current Content",
      description: "Run linter on current content",
      icon: "CheckCircle",
      hotkey: "Ctrl+Shift+L",
      execute: async (context: PluginContext) => {
        const linter = (globalThis as any).__craftLinter as ContentLinter;
        const issues = linter.lintContent(context.content);
        const counts = linter.getIssueCounts(issues);

        const message = `Linting complete: ${counts.error} errors, ${counts.warning} warnings, ${counts.info} suggestions`;
        context.showNotification("Lint Results", message);

        // In a real implementation, we'd show issues in a dedicated panel
        console.log("Lint issues:", issues);
      },
    },
    {
      id: "toggle-linter",
      name: "Toggle Linter",
      description: "Enable or disable the linter",
      icon: "ToggleLeft",
      execute: async (context: PluginContext) => {
        const linter = (globalThis as any).__craftLinter as ContentLinter;
        const wasEnabled = linter.isEnabled();
        linter.setEnabled(!wasEnabled);

        context.showNotification(
          "Linter Toggled",
          `Linter is now ${!wasEnabled ? "enabled" : "disabled"}`
        );
      },
    },
    {
      id: "show-lint-rules",
      name: "Show Lint Rules",
      description: "Show all available lint rules",
      icon: "List",
      execute: async (context: PluginContext) => {
        const linter = (globalThis as any).__craftLinter as ContentLinter;
        const rules = linter.getRules();

        const rulesByCategory = rules.reduce((acc, rule) => {
          if (!acc[rule.category]) acc[rule.category] = [];
          acc[rule.category].push(rule);
          return acc;
        }, {} as Record<string, LintRule[]>);

        let message = "Available Lint Rules:\n\n";
        for (const [category, categoryRules] of Object.entries(
          rulesByCategory
        )) {
          message += `**${category.toUpperCase()}**\n`;
          categoryRules.forEach((rule) => {
            message += `- ${rule.name}: ${rule.description}\n`;
          });
          message += "\n";
        }

        context.showNotification("Lint Rules", message);
      },
    },
  ],

  settings: {
    enabledByDefault: {
      type: "boolean",
      default: true,
      description: "Enable linter by default",
    },
    showInlineIssues: {
      type: "boolean",
      default: true,
      description: "Show lint issues inline in the editor",
    },
    maxIssuesShown: {
      type: "number",
      default: 50,
      description: "Maximum number of issues to show at once",
    },
  },
};
