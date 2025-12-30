// src/plugins/index.ts
// Core Plugin System for Craft IDE
// Inspired by Obsidian's plugin architecture but tailored for our needs

export interface PluginContext {
  content: string;
  setContent: (content: string) => void;
  mode: string;
  setMode: (mode: string) => void;
  addRef: (ref: any) => void;
  showNotification: (title: string, message: string) => void;
}

export interface PluginCommand {
  id: string;
  name: string;
  description: string;
  icon?: string;
  hotkey?: string;
  execute: (context: PluginContext) => Promise<void> | void;
}

export interface Plugin {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;

  // Plugin lifecycle
  onLoad?: (context: PluginContext) => Promise<void> | void;
  onUnload?: () => Promise<void> | void;

  // Commands that this plugin provides
  commands?: PluginCommand[];

  // Settings schema
  settings?: {
    [key: string]: {
      type: "string" | "number" | "boolean" | "select";
      default: any;
      options?: string[];
      description: string;
    };
  };
}

export class PluginManager {
  private plugins: Map<string, Plugin> = new Map();
  private context: PluginContext;
  private settings: Map<string, any> = new Map();

  constructor(context: PluginContext) {
    this.context = context;
  }

  async loadPlugin(plugin: Plugin): Promise<void> {
    try {
      // Initialize plugin settings with defaults
      if (plugin.settings) {
        const pluginSettings: any = {};
        for (const [key, setting] of Object.entries(plugin.settings)) {
          pluginSettings[key] = setting.default;
        }
        this.settings.set(plugin.id, pluginSettings);
      }

      // Call plugin's onLoad if it exists
      if (plugin.onLoad) {
        await plugin.onLoad(this.context);
      }

      this.plugins.set(plugin.id, plugin);
      console.log(`Plugin loaded: ${plugin.name} v${plugin.version}`);
    } catch (error) {
      console.error(`Failed to load plugin ${plugin.id}:`, error);
      throw error;
    }
  }

  async unloadPlugin(pluginId: string): Promise<void> {
    const plugin = this.plugins.get(pluginId);
    if (!plugin) return;

    try {
      if (plugin.onUnload) {
        await plugin.onUnload();
      }

      this.plugins.delete(pluginId);
      this.settings.delete(pluginId);
      console.log(`Plugin unloaded: ${plugin.name}`);
    } catch (error) {
      console.error(`Failed to unload plugin ${pluginId}:`, error);
    }
  }

  getPlugin(pluginId: string): Plugin | undefined {
    return this.plugins.get(pluginId);
  }

  getAllPlugins(): Plugin[] {
    return Array.from(this.plugins.values());
  }

  getAllCommands(): PluginCommand[] {
    const commands: PluginCommand[] = [];
    for (const plugin of this.plugins.values()) {
      if (plugin.commands) {
        commands.push(...plugin.commands);
      }
    }
    return commands;
  }

  async executeCommand(commandId: string): Promise<void> {
    for (const plugin of this.plugins.values()) {
      if (plugin.commands) {
        const command = plugin.commands.find((cmd) => cmd.id === commandId);
        if (command) {
          try {
            await command.execute(this.context);
            return;
          } catch (error) {
            console.error(`Failed to execute command ${commandId}:`, error);
            throw error;
          }
        }
      }
    }
    throw new Error(`Command not found: ${commandId}`);
  }

  getPluginSettings(pluginId: string): any {
    return this.settings.get(pluginId) || {};
  }

  setPluginSettings(pluginId: string, settings: any): void {
    this.settings.set(pluginId, settings);
  }
}

// Global plugin manager instance
let pluginManager: PluginManager | null = null;

export function initializePluginManager(context: PluginContext): PluginManager {
  pluginManager = new PluginManager(context);
  return pluginManager;
}

export function getPluginManager(): PluginManager {
  if (!pluginManager) {
    throw new Error("Plugin manager not initialized");
  }
  return pluginManager;
}
