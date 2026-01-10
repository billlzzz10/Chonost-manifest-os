// src/plugins/readMode.ts
// Read Mode Plugin - Enhanced reading experience with multiple view modes
// Provides different reading layouts and focus modes

import type { Plugin, PluginContext } from "./index";

type ReadModeType = "standard" | "focus" | "presentation" | "outline" | "zen";

interface ReadModeSettings {
  fontSize: number;
  lineHeight: number;
  maxWidth: number;
  theme: "light" | "dark" | "sepia" | "high-contrast";
  showWordCount: boolean;
  showReadingTime: boolean;
  hideUI: boolean;
}

class ReadModeManager {
  private context: PluginContext;
  private currentMode: ReadModeType = "standard";
  private settings: ReadModeSettings;
  private originalContent: string = "";

  constructor(context: PluginContext) {
    this.context = context;
    this.settings = {
      fontSize: 16,
      lineHeight: 1.6,
      maxWidth: 800,
      theme: "dark",
      showWordCount: true,
      showReadingTime: true,
      hideUI: false,
    };
  }

  async activateReadMode(mode: ReadModeType): Promise<void> {
    this.currentMode = mode;
    this.originalContent = this.context.content;

    // Switch to reading mode in the main app
    this.context.setMode("reading");

    // Apply mode-specific transformations
    switch (mode) {
      case "focus":
        await this.activateFocusMode();
        break;
      case "presentation":
        await this.activatePresentationMode();
        break;
      case "outline":
        await this.activateOutlineMode();
        break;
      case "zen":
        await this.activateZenMode();
        break;
      default:
        await this.activateStandardMode();
        break;
    }

    this.context.showNotification("Read Mode", `${mode} mode activated`);
  }

  private async activateStandardMode(): Promise<void> {
    // Standard reading mode - clean markdown rendering
    // No special transformations needed
  }

  private async activateFocusMode(): Promise<void> {
    // Focus mode - highlight current paragraph, dim others
    const content = this.processContentForFocus(this.originalContent);
    this.context.setContent(content);
  }

  private async activatePresentationMode(): Promise<void> {
    // Presentation mode - split content into slides
    const slides = this.createSlides(this.originalContent);
    const slideContent = this.formatAsSlides(slides);
    this.context.setContent(slideContent);
  }

  private async activateOutlineMode(): Promise<void> {
    // Outline mode - show only headings and structure
    const outline = this.extractOutline(this.originalContent);
    this.context.setContent(outline);
  }

  private async activateZenMode(): Promise<void> {
    // Zen mode - minimal distraction reading
    const cleanContent = this.cleanContentForZen(this.originalContent);
    this.context.setContent(cleanContent);
  }

  private processContentForFocus(content: string): string {
    // Add focus indicators to paragraphs
    const lines = content.split("\n");
    const processedLines = lines.map((line, index) => {
      if (line.trim() && !line.startsWith("#") && !line.startsWith("```")) {
        return `<div class="focus-paragraph" data-paragraph="${index}">${line}</div>`;
      }
      return line;
    });

    return processedLines.join("\n");
  }

  private createSlides(content: string): string[] {
    const slides: string[] = [];
    const lines = content.split("\n");
    let currentSlide: string[] = [];

    for (const line of lines) {
      // Start new slide on H1 or H2 headings
      if (line.match(/^#{1,2}\s/)) {
        if (currentSlide.length > 0) {
          slides.push(currentSlide.join("\n"));
          currentSlide = [];
        }
      }
      currentSlide.push(line);
    }

    if (currentSlide.length > 0) {
      slides.push(currentSlide.join("\n"));
    }

    return slides;
  }

  private formatAsSlides(slides: string[]): string {
    let slideContent = "# Presentation Mode\n\n";

    slides.forEach((slide, index) => {
      slideContent += `---\n\n## Slide ${index + 1}\n\n${slide}\n\n`;
    });

    slideContent += `\n\n---\n\n*Total slides: ${slides.length}*`;
    return slideContent;
  }

  private extractOutline(content: string): string {
    const lines = content.split("\n");
    const outlineLines: string[] = ["# Document Outline\n"];

    for (const line of lines) {
      const headingMatch = line.match(/^(#{1,6})\s(.+)/);
      if (headingMatch) {
        const level = headingMatch[1].length;
        const title = headingMatch[2];
        const indent = "  ".repeat(level - 1);
        outlineLines.push(`${indent}- ${title}`);
      }
    }

    // Add reading statistics
    const stats = this.calculateReadingStats(content);
    outlineLines.push("\n## Reading Statistics");
    outlineLines.push(`- Word count: ${stats.wordCount}`);
    outlineLines.push(`- Estimated reading time: ${stats.readingTime} minutes`);
    outlineLines.push(`- Paragraphs: ${stats.paragraphs}`);
    outlineLines.push(`- Headings: ${stats.headings}`);

    return outlineLines.join("\n");
  }

  private cleanContentForZen(content: string): string {
    // Remove distracting elements for zen reading
    let cleanContent = content;

    // Remove code blocks (replace with simplified version)
    cleanContent = cleanContent.replace(/```[\s\S]*?```/g, "*[Code block]*");

    // Remove complex markdown (links, images)
    cleanContent = cleanContent.replace(/!\[.*?\]\(.*?\)/g, "*[Image]*");
    cleanContent = cleanContent.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");

    // Remove excessive formatting
    cleanContent = cleanContent.replace(/\*\*\*(.*?)\*\*\*/g, "$1");
    cleanContent = cleanContent.replace(/\*\*(.*?)\*\*/g, "$1");
    cleanContent = cleanContent.replace(/\*(.*?)\*/g, "$1");

    return cleanContent;
  }

  private calculateReadingStats(content: string) {
    const text = content.replace(/[#*`\[\]()]/g, ""); // Remove markdown
    const words = text.split(/\s+/).filter((word) => word.length > 0);
    const paragraphs = content
      .split(/\n\s*\n/)
      .filter((p) => p.trim().length > 0);
    const headings = (content.match(/^#{1,6}\s/gm) || []).length;

    return {
      wordCount: words.length,
      readingTime: Math.ceil(words.length / 200), // Average reading speed
      paragraphs: paragraphs.length,
      headings,
    };
  }

  async exitReadMode(): Promise<void> {
    // Restore original content
    this.context.setContent(this.originalContent);
    this.context.setMode("editor");
    this.currentMode = "standard";

    this.context.showNotification("Read Mode", "Exited read mode");
  }

  getCurrentMode(): ReadModeType {
    return this.currentMode;
  }

  updateSettings(newSettings: Partial<ReadModeSettings>): void {
    this.settings = { ...this.settings, ...newSettings };
  }

  getSettings(): ReadModeSettings {
    return { ...this.settings };
  }

  async toggleReadingStats(): Promise<void> {
    const stats = this.calculateReadingStats(this.context.content);
    const message = `
Word Count: ${stats.wordCount}
Reading Time: ${stats.readingTime} minutes
Paragraphs: ${stats.paragraphs}
Headings: ${stats.headings}
    `.trim();

    this.context.showNotification("Reading Statistics", message);
  }
}

export const readModePlugin: Plugin = {
  id: "read-mode",
  name: "Enhanced Read Mode",
  version: "1.0.0",
  description: "Provides enhanced reading experience with multiple view modes",
  author: "Craft IDE Team",

  onLoad: async (context: PluginContext) => {
    const readMode = new ReadModeManager(context);

    // Store read mode instance for command access
    (globalThis as any).__craftReadMode = readMode;
  },

  commands: [
    {
      id: "activate-standard-read",
      name: "Standard Read Mode",
      description: "Activate standard reading mode",
      icon: "BookOpen",
      hotkey: "Ctrl+Shift+R",
      execute: async (context: PluginContext) => {
        const readMode = (globalThis as any).__craftReadMode as ReadModeManager;
        await readMode.activateReadMode("standard");
      },
    },
    {
      id: "activate-focus-read",
      name: "Focus Read Mode",
      description: "Activate focus reading mode with paragraph highlighting",
      icon: "Target",
      execute: async (context: PluginContext) => {
        const readMode = (globalThis as any).__craftReadMode as ReadModeManager;
        await readMode.activateReadMode("focus");
      },
    },
    {
      id: "activate-presentation-mode",
      name: "Presentation Mode",
      description: "Split content into presentation slides",
      icon: "Presentation",
      execute: async (context: PluginContext) => {
        const readMode = (globalThis as any).__craftReadMode as ReadModeManager;
        await readMode.activateReadMode("presentation");
      },
    },
    {
      id: "activate-outline-mode",
      name: "Outline Mode",
      description: "Show document outline and structure",
      icon: "List",
      execute: async (context: PluginContext) => {
        const readMode = (globalThis as any).__craftReadMode as ReadModeManager;
        await readMode.activateReadMode("outline");
      },
    },
    {
      id: "activate-zen-mode",
      name: "Zen Read Mode",
      description: "Minimal distraction reading mode",
      icon: "Minimize",
      execute: async (context: PluginContext) => {
        const readMode = (globalThis as any).__craftReadMode as ReadModeManager;
        await readMode.activateReadMode("zen");
      },
    },
    {
      id: "exit-read-mode",
      name: "Exit Read Mode",
      description: "Return to editor mode",
      icon: "X",
      hotkey: "Escape",
      execute: async (context: PluginContext) => {
        const readMode = (globalThis as any).__craftReadMode as ReadModeManager;
        await readMode.exitReadMode();
      },
    },
    {
      id: "show-reading-stats",
      name: "Show Reading Statistics",
      description: "Display word count and reading time",
      icon: "BarChart",
      hotkey: "Ctrl+Shift+S",
      execute: async (context: PluginContext) => {
        const readMode = (globalThis as any).__craftReadMode as ReadModeManager;
        await readMode.toggleReadingStats();
      },
    },
  ],

  settings: {
    defaultMode: {
      type: "select",
      default: "standard",
      options: ["standard", "focus", "presentation", "outline", "zen"],
      description: "Default read mode when activated",
    },
    fontSize: {
      type: "number",
      default: 16,
      description: "Font size for reading mode (px)",
    },
    lineHeight: {
      type: "number",
      default: 1.6,
      description: "Line height for reading mode",
    },
    maxWidth: {
      type: "number",
      default: 800,
      description: "Maximum content width for reading (px)",
    },
    autoShowStats: {
      type: "boolean",
      default: true,
      description: "Automatically show reading statistics",
    },
  },
};
