import { create } from 'zustand';

interface Document {
  id: string;
  title: string;
  content: string;
  file_path?: string;
  file_type?: string;
  created_at: string;
  updated_at?: string;
}

interface Todo {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at?: string;
  due_date?: string;
}

interface AppState {
  // Current view state
  currentView: 'editor' | 'whiteboard';

  // Document state
  currentDocument: Document | null;
  documents: Document[];

  // Todo state
  todos: Todo[];
  isTodoPanelOpen: boolean;

  // UI state
  isSidebarOpen: boolean;
  isAssistantOpen: boolean;
  
  // Actions
  setCurrentView: (view: 'editor' | 'whiteboard') => void;
  setCurrentDocument: (document: Document | null) => void;
  setDocuments: (documents: Document[]) => void;
  toggleSidebar: () => void;
  toggleAssistant: () => void;
  toggleTodoPanel: () => void;

  // Document actions
  createDocument: (title: string, content?: string) => Promise<Document>;
  updateDocument: (id: string, updates: Partial<Document>) => Promise<void>;
  deleteDocument: (id: string) => Promise<void>;
  saveDocument: () => Promise<void>;

  // Todo actions
  createTodo: (title: string, description?: string, priority?: 'low' | 'medium' | 'high') => Promise<Todo>;
  updateTodo: (id: string, updates: Partial<Todo>) => Promise<void>;
  deleteTodo: (id: string) => Promise<void>;
  toggleTodoStatus: (id: string) => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state
  currentView: 'editor',
  currentDocument: null,
  documents: [],
  todos: [],
  isSidebarOpen: true,
  isAssistantOpen: false,
  isTodoPanelOpen: false,

  // Actions
  setCurrentView: (view) => set({ currentView: view }),
  
  setCurrentDocument: (document) => set({ currentDocument: document }),
  
  setDocuments: (documents) => set({ documents }),
  
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

  toggleAssistant: () => set((state) => ({ isAssistantOpen: !state.isAssistantOpen })),

  toggleTodoPanel: () => set((state) => ({ isTodoPanelOpen: !state.isTodoPanelOpen })),

  // Document actions
  createDocument: async (title, content = '') => {
    const newDocument: Document = {
      id: Date.now().toString(),
      title,
      content,
      created_at: new Date().toISOString(),
    };
    
    set((state) => ({
      documents: [...state.documents, newDocument],
      currentDocument: newDocument,
    }));
    
    return newDocument;
  },

  updateDocument: async (id, updates) => {
    set((state) => ({
      documents: state.documents.map((doc) =>
        doc.id === id ? { ...doc, ...updates, updated_at: new Date().toISOString() } : doc
      ),
      currentDocument: state.currentDocument?.id === id 
        ? { ...state.currentDocument, ...updates, updated_at: new Date().toISOString() }
        : state.currentDocument,
    }));
  },

  deleteDocument: async (id) => {
    set((state) => ({
      documents: state.documents.filter((doc) => doc.id !== id),
      currentDocument: state.currentDocument?.id === id ? null : state.currentDocument,
    }));
  },

  saveDocument: async () => {
    const { currentDocument } = get();
    if (currentDocument) {
      await get().updateDocument(currentDocument.id, {
        content: currentDocument.content,
      });
    }
  },

  // Todo actions
  createTodo: async (title, description = '', priority = 'medium' as const) => {
    const newTodo: Todo = {
      id: Date.now().toString(),
      title,
      description,
      status: 'pending',
      priority,
      created_at: new Date().toISOString(),
    };

    set((state) => ({
      todos: [...state.todos, newTodo],
    }));

    return newTodo;
  },

  updateTodo: async (id, updates) => {
    set((state) => ({
      todos: state.todos.map((todo) =>
        todo.id === id ? { ...todo, ...updates, updated_at: new Date().toISOString() } : todo
      ),
    }));
  },

  deleteTodo: async (id) => {
    set((state) => ({
      todos: state.todos.filter((todo) => todo.id !== id),
    }));
  },

  toggleTodoStatus: async (id) => {
    set((state) => ({
      todos: state.todos.map((todo) =>
        todo.id === id
          ? {
              ...todo,
              status: todo.status === 'completed' ? 'pending' : 'completed',
              updated_at: new Date().toISOString()
            }
          : todo
      ),
    }));
  },
}));
