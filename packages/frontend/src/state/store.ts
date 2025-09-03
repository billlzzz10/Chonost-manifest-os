import { create } from "zustand";
import { persist } from "zustand/middleware";

// Types
export interface PaletteItem {
  id: string;
  type: "color" | "tool" | "command" | "script";
  label: string;
  icon: string; // lucide:icon-name or logo:brand-name
  color?: string;
  value?: string;
  gradient?: boolean;
}

export interface AppState {
  // Theme
  theme: "light" | "dark";
  setTheme: (theme: "light" | "dark") => void;
  toggleTheme: () => void;

  // Current View
  currentView: "editor" | "whiteboard" | "chat" | "files" | "settings";
  setCurrentView: (
    view: "editor" | "whiteboard" | "chat" | "files" | "settings"
  ) => void;

  // Rotary Palettes
  leftPalette: PaletteItem[];
  rightPalette: PaletteItem[];
  addPaletteItem: (side: "left" | "right", item: PaletteItem) => void;
  removePaletteItem: (side: "left" | "right", id: string) => void;
  updatePaletteItem: (
    side: "left" | "right",
    id: string,
    updates: Partial<PaletteItem>
  ) => void;

  // UI State
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;

  // Notifications
  notifications: Notification[];
  addNotification: (
    notification: Omit<Notification, "id" | "timestamp">
  ) => void;
  removeNotification: (id: string) => void;
  markNotificationAsRead: (id: string) => void;

  // Current Document
  currentManuscript?: Manuscript;
  setCurrentManuscript: (manuscript?: Manuscript) => void;

  // Chat
  currentChatSession?: ChatSession;
  setCurrentChatSession: (session?: ChatSession) => void;
}

export interface Notification {
  id: string;
  type: "info" | "success" | "warning" | "error";
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface Manuscript {
  id: string;
  title: string;
  content: string;
  author: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: "user" | "assistant";
  timestamp: Date;
}

// Default Palette Items
const defaultLeftPalette: PaletteItem[] = [
  // Colors
  {
    id: "c-red",
    type: "color",
    label: "Red",
    icon: "lucide:circle",
    color: "#ef4444",
    gradient: true,
  },
  {
    id: "c-orange",
    type: "color",
    label: "Orange",
    icon: "lucide:circle",
    color: "#f97316",
    gradient: true,
  },
  {
    id: "c-yellow",
    type: "color",
    label: "Yellow",
    icon: "lucide:circle",
    color: "#facc15",
    gradient: true,
  },
  {
    id: "c-green",
    type: "color",
    label: "Green",
    icon: "lucide:circle",
    color: "#22c55e",
    gradient: true,
  },
  {
    id: "c-blue",
    type: "color",
    label: "Blue",
    icon: "lucide:circle",
    color: "#3b82f6",
    gradient: true,
  },
  {
    id: "c-purple",
    type: "color",
    label: "Purple",
    icon: "lucide:circle",
    color: "#a855f7",
    gradient: true,
  },

  // Tools
  {
    id: "pen",
    type: "tool",
    label: "Pen",
    icon: "lucide:edit-3",
    value: "pen",
    gradient: true,
  },
  {
    id: "eraser",
    type: "tool",
    label: "Eraser",
    icon: "lucide:eraser",
    value: "eraser",
    gradient: true,
  },
  {
    id: "ruler",
    type: "tool",
    label: "Ruler",
    icon: "lucide:ruler",
    value: "ruler",
    gradient: true,
  },
  {
    id: "note",
    type: "tool",
    label: "Note",
    icon: "lucide:sticky-note",
    value: "add-note",
    gradient: true,
  },
];

const defaultRightPalette: PaletteItem[] = [
  // Commands
  {
    id: "toggle",
    type: "command",
    label: "Toggle Mode",
    icon: "lucide:refresh-cw",
    value: "toggle-mode",
    gradient: true,
  },
  {
    id: "analyze",
    type: "command",
    label: "Analyze",
    icon: "lucide:bar-chart-2",
    value: "analyze",
    gradient: true,
  },
  {
    id: "script",
    type: "command",
    label: "Script",
    icon: "lucide:terminal",
    value: "run-script",
    gradient: true,
  },
  {
    id: "export",
    type: "command",
    label: "Export",
    icon: "lucide:download",
    value: "export",
    gradient: true,
  },

  // Brand Icons
  {
    id: "github",
    type: "command",
    label: "GitHub",
    icon: "logo:github",
    value: "open-github",
    gradient: true,
  },
  {
    id: "figma",
    type: "command",
    label: "Figma",
    icon: "logo:figma",
    value: "open-figma",
    gradient: true,
  },
  {
    id: "notion",
    type: "command",
    label: "Notion",
    icon: "logo:notion",
    value: "open-notion",
    gradient: true,
  },
];

// Create Store
export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Theme
      theme: "dark",
      setTheme: (theme) => {
        set({ theme });
        // Update document root class for CSS variables
        document.documentElement.className = theme;
      },
      toggleTheme: () => {
        const currentTheme = get().theme;
        const newTheme = currentTheme === "light" ? "dark" : "light";
        get().setTheme(newTheme);
      },

      // Current View
      currentView: "editor",
      setCurrentView: (view) => set({ currentView: view }),

      // Rotary Palettes
      leftPalette: defaultLeftPalette,
      rightPalette: defaultRightPalette,
      addPaletteItem: (side, item) => {
        if (side === "left") {
          set((state) => ({
            leftPalette: [...state.leftPalette, item],
          }));
        } else {
          set((state) => ({
            rightPalette: [...state.rightPalette, item],
          }));
        }
      },
      removePaletteItem: (side, id) => {
        if (side === "left") {
          set((state) => ({
            leftPalette: state.leftPalette.filter((item) => item.id !== id),
          }));
        } else {
          set((state) => ({
            rightPalette: state.rightPalette.filter((item) => item.id !== id),
          }));
        }
      },
      updatePaletteItem: (side, id, updates) => {
        if (side === "left") {
          set((state) => ({
            leftPalette: state.leftPalette.map((item) =>
              item.id === id ? { ...item, ...updates } : item
            ),
          }));
        } else {
          set((state) => ({
            rightPalette: state.rightPalette.map((item) =>
              item.id === id ? { ...item, ...updates } : item
            ),
          }));
        }
      },

      // UI State
      sidebarCollapsed: false,
      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

      // Notifications
      notifications: [],
      addNotification: (notification) => {
        const newNotification: Notification = {
          ...notification,
          id: Date.now().toString(),
          timestamp: new Date(),
          read: false,
        };
        set((state) => ({
          notifications: [newNotification, ...state.notifications],
        }));
      },
      removeNotification: (id) => {
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        }));
      },
      markNotificationAsRead: (id) => {
        set((state) => ({
          notifications: state.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n
          ),
        }));
      },

      // Current Document
      currentManuscript: undefined,
      setCurrentManuscript: (manuscript) =>
        set({ currentManuscript: manuscript }),

      // Chat
      currentChatSession: undefined,
      setCurrentChatSession: (session) => set({ currentChatSession: session }),
    }),
    {
      name: "chonost-app-store",
      partialize: (state) => ({
        theme: state.theme,
        leftPalette: state.leftPalette,
        rightPalette: state.rightPalette,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);

// Initialize theme on app start
if (typeof window !== "undefined") {
  const savedTheme = localStorage.getItem("chonost-app-store");
  if (savedTheme) {
    try {
      const parsed = JSON.parse(savedTheme);
      if (parsed.state?.theme) {
        document.documentElement.className = parsed.state.theme;
      }
    } catch (e) {
      console.warn("Failed to parse saved theme");
    }
  }
}

export default useAppStore;
