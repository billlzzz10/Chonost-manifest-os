// src/state/store.ts
// Zustand store for Craft IDE application state
import { create } from "zustand";

export interface Reference {
  id: string;
  title: string;
  kind: "file" | "url" | "note";
  url: string;
  createdAt: number;
}

export interface AppState {
  // Content management
  content: string;
  setContent: (content: string) => void;

  // Mode management
  mode: "editor" | "whiteboard" | "reading";
  setMode: (mode: "editor" | "whiteboard" | "reading") => void;

  // References
  refs: Reference[];
  addRef: (ref: Reference) => void;
  removeRef: (id: string) => void;

  // UI state
  showLeftPanel: boolean;
  showRightPanel: boolean;
  toggleLeftPanel: () => void;
  toggleRightPanel: () => void;

  // Settings
  theme: "light" | "dark";
  toggleTheme: () => void;

  // Notifications
  notifications: string[];
  addNotification: (message: string) => void;
  clearNotifications: () => void;
}

export const useStore = create<AppState>((set, get) => ({
  // Content management
  content: "",
  setContent: (content: string) => set({ content }),

  // Mode management
  mode: "editor",
  setMode: (mode: "editor" | "whiteboard" | "reading") => set({ mode }),

  // References
  refs: [],
  addRef: (ref: Reference) =>
    set((state) => ({
      refs: [...state.refs, ref],
    })),
  removeRef: (id: string) =>
    set((state) => ({
      refs: state.refs.filter((ref) => ref.id !== id),
    })),

  // UI state
  showLeftPanel: true,
  showRightPanel: true,
  toggleLeftPanel: () =>
    set((state) => ({
      showLeftPanel: !state.showLeftPanel,
    })),
  toggleRightPanel: () =>
    set((state) => ({
      showRightPanel: !state.showRightPanel,
    })),

  // Settings
  theme: "dark",
  toggleTheme: () =>
    set((state) => ({
      theme: state.theme === "light" ? "dark" : "light",
    })),

  // Notifications
  notifications: [],
  addNotification: (message: string) =>
    set((state) => ({
      notifications: [...state.notifications, message],
    })),
  clearNotifications: () => set({ notifications: [] }),
}));

// Export individual selectors for better performance
export const useContent = () => useStore((state) => state.content);
export const useSetContent = () => useStore((state) => state.setContent);
export const useMode = () => useStore((state) => state.mode);
export const useSetMode = () => useStore((state) => state.setMode);
export const useRefs = () => useStore((state) => state.refs);
export const useAddRef = () => useStore((state) => state.addRef);
export const useRemoveRef = () => useStore((state) => state.removeRef);
export const useTheme = () => useStore((state) => state.theme);
export const useToggleTheme = () => useStore((state) => state.toggleTheme);
export const useNotifications = () => useStore((state) => state.notifications);
export const useAddNotification = () =>
  useStore((state) => state.addNotification);
export const useClearNotifications = () =>
  useStore((state) => state.clearNotifications);
