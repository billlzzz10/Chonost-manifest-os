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

interface AppState {
  // Current view state
  currentView: 'editor' | 'whiteboard';
  
  // Document state
  currentDocument: Document | null;
  documents: Document[];
  
  // UI state
  isSidebarOpen: boolean;
  isAssistantOpen: boolean;
  
  // Actions
  setCurrentView: (view: 'editor' | 'whiteboard') => void;
  setCurrentDocument: (document: Document | null) => void;
  setDocuments: (documents: Document[]) => void;
  toggleSidebar: () => void;
  toggleAssistant: () => void;
  
  // Document actions
  createDocument: (title: string, content?: string) => Promise<Document>;
  updateDocument: (id: string, updates: Partial<Document>) => Promise<void>;
  deleteDocument: (id: string) => Promise<void>;
  saveDocument: () => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state
  currentView: 'editor',
  currentDocument: null,
  documents: [],
  isSidebarOpen: true,
  isAssistantOpen: false,

  // Actions
  setCurrentView: (view) => set({ currentView: view }),
  
  setCurrentDocument: (document) => set({ currentDocument: document }),
  
  setDocuments: (documents) => set({ documents }),
  
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  
  toggleAssistant: () => set((state) => ({ isAssistantOpen: !state.isAssistantOpen })),

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
}));
