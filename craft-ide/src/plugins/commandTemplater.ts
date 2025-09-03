// src/plugins/commandTemplater.ts
// Command Templater Plugin - Inspired by Obsidian's Templater
// Provides template functionality with dynamic content generation

import type { Plugin, PluginContext } from "./index";

interface Template {
  id: string;
  name: string;
  content: string;
  variables?: string[];
  description?: string;
}

class CommandTemplater {
  private templates: Map<string, Template> = new Map();
  private context: PluginContext;

  constructor(context: PluginContext) {
    this.context = context;
    this.initializeDefaultTemplates();
  }

  private initializeDefaultTemplates() {
    const defaultTemplates: Template[] = [
      {
        id: "daily-note",
        name: "Daily Note",
        content: `# Daily Note - {{date}}

## Today's Goals
- [ ] 

## Notes


## Reflections


---
Created: {{time}}`,
        variables: ["date", "time"],
        description: "Create a daily note template",
      },
      {
        id: "meeting-notes",
        name: "Meeting Notes",
        content: `# Meeting: {{title}}

**Date:** {{date}}
**Time:** {{time}}
**Attendees:** {{attendees}}

## Agenda
1. 

## Discussion


## Action Items
- [ ] 

## Next Steps


---
Meeting notes created: {{timestamp}}`,
        variables: ["title", "date", "time", "attendees", "timestamp"],
        description: "Template for meeting notes",
      },
      {
        id: "project-outline",
        name: "Project Outline",
        content: `# Project: {{project_name}}

## Overview
{{description}}

## Objectives
- 

## Timeline
- **Start Date:** {{start_date}}
- **End Date:** {{end_date}}

## Resources
- 

## Milestones
1. 

## Risks & Mitigation
- 

---
Project created: {{timestamp}}`,
        variables: [
          "project_name",
          "description",
          "start_date",
          "end_date",
          "timestamp",
        ],
        description: "Template for project planning",
      },
      {
        id: "code-snippet",
        name: "Code Snippet",
        content: `# {{title}}

## Description
{{description}}

## Code
\`\`\`{{language}}
{{code}}
\`\`\`

## Usage
{{usage}}

## Notes
{{notes}}

---
Tags: {{tags}}
Created: {{timestamp}}`,
        variables: [
          "title",
          "description",
          "language",
          "code",
          "usage",
          "notes",
          "tags",
          "timestamp",
        ],
        description: "Template for code snippets",
      },
    ];

    defaultTemplates.forEach((template) => {
      this.templates.set(template.id, template);
    });
  }

  private async promptForVariables(
    variables: string[]
  ): Promise<Record<string, string>> {
    const values: Record<string, string> = {};

    for (const variable of variables) {
      let value = "";

      // Handle special variables with auto-generation
      switch (variable) {
        case "date":
          value = new Date().toLocaleDateString();
          break;
        case "time":
          value = new Date().toLocaleTimeString();
          break;
        case "timestamp":
          value = new Date().toISOString();
          break;
        default:
          // For other variables, we would normally prompt the user
          // For now, we'll use placeholder values
          value = prompt(`Enter value for ${variable}:`) || `{{${variable}}}`;
          break;
      }

      values[variable] = value;
    }

    return values;
  }

  private processTemplate(
    template: Template,
    variables: Record<string, string>
  ): string {
    let content = template.content;

    // Replace variables in the template
    for (const [key, value] of Object.entries(variables)) {
      const regex = new RegExp(`{{${key}}}`, "g");
      content = content.replace(regex, value);
    }

    return content;
  }

  async insertTemplate(templateId: string): Promise<void> {
    const template = this.templates.get(templateId);
    if (!template) {
      throw new Error(`Template not found: ${templateId}`);
    }

    try {
      // Get variable values
      const variables = await this.promptForVariables(template.variables || []);

      // Process template
      const processedContent = this.processTemplate(template, variables);

      // Insert into editor
      const currentContent = this.context.content;
      const newContent = currentContent + "\n\n" + processedContent;
      this.context.setContent(newContent);

      this.context.showNotification(
        "Template Inserted",
        `${template.name} template has been inserted`
      );
    } catch (error) {
      console.error("Failed to insert template:", error);
      this.context.showNotification("Error", "Failed to insert template");
    }
  }

  async createCustomTemplate(): Promise<void> {
    const name = prompt("Template name:");
    if (!name) return;

    const content = prompt(
      "Template content (use {{variable}} for placeholders):"
    );
    if (!content) return;

    // Extract variables from template content
    const variableMatches = content.match(/{{(\w+)}}/g);
    const variables = variableMatches
      ? [...new Set(variableMatches.map((match) => match.slice(2, -2)))]
      : [];

    const template: Template = {
      id: `custom-${Date.now()}`,
      name,
      content,
      variables,
      description: "Custom user template",
    };

    this.templates.set(template.id, template);
    this.context.showNotification(
      "Template Created",
      `Custom template "${name}" has been created`
    );
  }

  getTemplates(): Template[] {
    return Array.from(this.templates.values());
  }

  deleteTemplate(templateId: string): void {
    if (templateId.startsWith("custom-")) {
      this.templates.delete(templateId);
      this.context.showNotification(
        "Template Deleted",
        "Custom template has been deleted"
      );
    } else {
      this.context.showNotification("Error", "Cannot delete default templates");
    }
  }
}

export const commandTemplaterPlugin: Plugin = {
  id: "command-templater",
  name: "Command Templater",
  version: "1.0.0",
  description:
    "Provides template functionality with dynamic content generation",
  author: "Craft IDE Team",

  onLoad: async (context: PluginContext) => {
    const templater = new CommandTemplater(context);

    // Store templater instance for command access
    (globalThis as any).__craftTemplater = templater;
  },

  commands: [
    {
      id: "insert-daily-note",
      name: "Insert Daily Note Template",
      description: "Insert a daily note template",
      icon: "Calendar",
      hotkey: "Ctrl+Shift+D",
      execute: async (context: PluginContext) => {
        const templater = (globalThis as any)
          .__craftTemplater as CommandTemplater;
        await templater.insertTemplate("daily-note");
      },
    },
    {
      id: "insert-meeting-notes",
      name: "Insert Meeting Notes Template",
      description: "Insert a meeting notes template",
      icon: "Users",
      hotkey: "Ctrl+Shift+M",
      execute: async (context: PluginContext) => {
        const templater = (globalThis as any)
          .__craftTemplater as CommandTemplater;
        await templater.insertTemplate("meeting-notes");
      },
    },
    {
      id: "insert-project-outline",
      name: "Insert Project Outline Template",
      description: "Insert a project outline template",
      icon: "FolderOpen",
      execute: async (context: PluginContext) => {
        const templater = (globalThis as any)
          .__craftTemplater as CommandTemplater;
        await templater.insertTemplate("project-outline");
      },
    },
    {
      id: "insert-code-snippet",
      name: "Insert Code Snippet Template",
      description: "Insert a code snippet template",
      icon: "Code",
      execute: async (context: PluginContext) => {
        const templater = (globalThis as any)
          .__craftTemplater as CommandTemplater;
        await templater.insertTemplate("code-snippet");
      },
    },
    {
      id: "create-custom-template",
      name: "Create Custom Template",
      description: "Create a new custom template",
      icon: "Plus",
      execute: async (context: PluginContext) => {
        const templater = (globalThis as any)
          .__craftTemplater as CommandTemplater;
        await templater.createCustomTemplate();
      },
    },
    {
      id: "show-templates",
      name: "Show All Templates",
      description: "Show list of available templates",
      icon: "List",
      execute: async (context: PluginContext) => {
        const templater = (globalThis as any)
          .__craftTemplater as CommandTemplater;
        const templates = templater.getTemplates();
        const templateList = templates
          .map((t) => `- ${t.name}: ${t.description || "No description"}`)
          .join("\n");
        context.showNotification("Available Templates", templateList);
      },
    },
  ],

  settings: {
    autoInsertDate: {
      type: "boolean",
      default: true,
      description: "Automatically insert current date in templates",
    },
    dateFormat: {
      type: "select",
      default: "MM/DD/YYYY",
      options: ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"],
      description: "Date format for templates",
    },
  },
};
