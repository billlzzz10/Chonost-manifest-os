import { create } from 'zustand';

interface Task {
  id: string;
  title: string;
  progress: number;
  status: 'running' | 'done' | 'error';
}

interface Note {
  id: string;
  x: number;
  y: number;
  text: string;
}

interface PaletteItem {
  kind: string;
  label?: string;
}

interface CanvasObject {
  id: string;
  type: 'rectangle' | 'circle' | 'line' | 'arrow' | 'text';
  x: number;
  y: number;
  width?: number;
  height?: number;
  startX?: number;
  startY?: number;
  endX?: number;
  endY?: number;
  text?: string;
  color: string;
  strokeWidth: number;
  layerId: string;
  zIndex: number;
}

interface Layer {
  id: string;
  name: string;
  visible: boolean;
  locked: boolean;
  zIndex: number;
}

interface AppState {
  // Theme and app settings
  theme: 'light' | 'dark';
  currentFile: string | null;
  files: string[];
  isTauri: boolean;

  // Editor state
  mode: 'editor' | 'whiteboard' | 'reading';
  content: string;
  tool: 'pen' | 'erase' | 'ruler' | 'select' | 'rectangle' | 'circle' | 'line' | 'arrow' | 'text';
  penColor: string;

  // Canvas objects and layers
  canvasObjects: CanvasObject[];
  layers: Layer[];
  selectedObjectId: string | null;
  currentLayerId: string;

  // Tasks and notes
  tasks: Task[];
  notes: Note[];

  // Palette items
  leftPalette: PaletteItem[];
  rightPalette: PaletteItem[];

  // Data for dashboard
  data: {
    sentiment: number;
    wordCount: number;
    topKeywords: { keyword: string; weight: number }[];
  };

  // RAG Ingestion state
  isIngesting: boolean;

  // Actions
  setTheme: (theme: 'light' | 'dark') => void;
  setCurrentFile: (file: string | null) => void;
  setFiles: (files: string[]) => void;
  setIsTauri: (isTauri: boolean) => void;
  setMode: (mode: 'editor' | 'whiteboard' | 'reading') => void;
  setContent: (content: string) => void;
  setTool: (tool: 'pen' | 'erase' | 'ruler' | 'select' | 'rectangle' | 'circle' | 'line' | 'arrow' | 'text') => void;
  setPenColor: (color: string) => void;
  enqueue: (task: Task) => void;
  updateTask: (id: string, updates: Partial<Task>) => void;
  addNote: (note: Partial<Note>) => void;
  updateNote: (id: string, updates: Partial<Note>) => void;
  removeNote: (id: string) => void;
  setData: (data: any) => void;
  setIsIngesting: (isIngesting: boolean) => void;

  // Canvas actions
  addCanvasObject: (obj: Omit<CanvasObject, 'id'>) => void;
  updateCanvasObject: (id: string, updates: Partial<CanvasObject>) => void;
  removeCanvasObject: (id: string) => void;
  setSelectedObjectId: (id: string | null) => void;
  addLayer: (layer: Omit<Layer, 'id'>) => void;
  updateLayer: (id: string, updates: Partial<Layer>) => void;
  removeLayer: (id: string) => void;
  setCurrentLayerId: (id: string) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  theme: 'dark',
  currentFile: null,
  files: [],
  isTauri: false,
  mode: 'reading',
  content: `# Test Mermaid Diagrams

This is a test of Mermaid diagram rendering in Reading View.

## Flowchart

\`\`\`mermaid
graph TD;
   A-->B;
   A-->C;
   B-->D;
   C-->D;
\`\`\`

## Sequence Diagram

\`\`\`mermaid
sequenceDiagram
   participant Alice
   participant Bob
   Alice->>Bob: Hello Bob, how are you?
   Bob-->>Alice: I am good thanks!
\`\`\`

## Gantt Chart

\`\`\`mermaid
gantt
   title A Gantt Diagram
   dateFormat YYYY-MM-DD
   section Section
   A task          :a1, 2014-01-01, 30d
   Another task    :after a1, 20d
   section Another
   Task in sec     :2014-01-12, 12d
   another task    :24d
\`\`\`
`,
  tool: 'pen',
  penColor: '#ffffff',
  canvasObjects: [],
  layers: [{ id: 'default', name: 'Default Layer', visible: true, locked: false, zIndex: 0 }],
  selectedObjectId: null,
  currentLayerId: 'default',
  tasks: [],
  notes: [],
  leftPalette: [
    { kind: 'generate', label: 'G' },
    { kind: 'chat', label: 'C' },
    { kind: 'analyze', label: 'Y' },
    { kind: 'pen', label: 'Pen' },
    { kind: 'erase', label: 'Erase' },
    { kind: 'analyze', label: 'Analyze' }
  ],
  rightPalette: [
    { kind: 'ruler', label: 'Ruler' },
    { kind: 'script', label: 'Script' },
    { kind: 'clear', label: 'Clear' },
    { kind: 'pink', label: 'Pink' },
    { kind: 'orange', label: 'Orange' },
    { kind: 'white', label: 'White' }
  ],
  data: {
    sentiment: 0,
    wordCount: 0,
    topKeywords: []
  },
  isIngesting: false,

  setTheme: (theme) => set({ theme }),
  setCurrentFile: (file) => set({ currentFile: file }),
  setFiles: (files) => set({ files }),
  setIsTauri: (isTauri) => set({ isTauri }),
  setMode: (mode) => set({ mode }),
  setContent: (content) => set({ content }),
  setTool: (tool) => set({ tool }),
  setPenColor: (color) => set({ penColor: color }),
  enqueue: (task) => set((state) => ({ tasks: [...state.tasks, task] })),
  updateTask: (id, updates) => set((state) => ({
    tasks: state.tasks.map(t => t.id === id ? { ...t, ...updates } : t)
  })),
  addNote: (note) => set((state) => ({
    notes: [...state.notes, {
      id: note.id || `note-${Date.now()}`,
      x: note.x || 24,
      y: note.y || 24,
      text: note.text || 'note'
    }]
  })),
  updateNote: (id, updates) => set((state) => ({
    notes: state.notes.map(n => n.id === id ? { ...n, ...updates } : n)
  })),
  removeNote: (id) => set((state) => ({
    notes: state.notes.filter(n => n.id !== id)
  })),
  setData: (data) => set({ data }),
  setIsIngesting: (isIngesting) => set({ isIngesting }),

  // Canvas actions
  addCanvasObject: (obj) => set((state) => ({
    canvasObjects: [...state.canvasObjects, {
      ...obj,
      id: `obj-${Date.now()}-${typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2, 11)}`
    }]
  })),
  updateCanvasObject: (id, updates) => set((state) => ({
    canvasObjects: state.canvasObjects.map(obj =>
      obj.id === id ? { ...obj, ...updates } : obj
    )
  })),
  removeCanvasObject: (id) => set((state) => ({
    canvasObjects: state.canvasObjects.filter(obj => obj.id !== id),
    selectedObjectId: state.selectedObjectId === id ? null : state.selectedObjectId
  })),
  setSelectedObjectId: (id) => set({ selectedObjectId: id }),
  addLayer: (layer) => set((state) => ({
    layers: [...state.layers, {
      ...layer,
      id: `layer-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    }]
  })),
  updateLayer: (id, updates) => set((state) => ({
    layers: state.layers.map(layer =>
      layer.id === id ? { ...layer, ...updates } : layer
    )
  })),
  removeLayer: (id) => set((state) => ({
    layers: state.layers.filter(layer => layer.id !== id),
    canvasObjects: state.canvasObjects.filter(obj => obj.layerId !== id),
    currentLayerId: state.currentLayerId === id ? 'default' : state.currentLayerId
  })),
  setCurrentLayerId: (id) => set({ currentLayerId: id }),
}));
