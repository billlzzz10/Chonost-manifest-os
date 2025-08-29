/**
 * File Entity Model
 * 
 * This module defines the File entity and related operations.
 */

import { create } from 'zustand';
import { fileApi } from '../../shared/api/client';

// File store using Zustand
export const useFileStore = create((set, get) => ({
  // State
  files: [],
  currentFile: null,
  isLoading: false,
  error: null,
  uploadProgress: {},

  // Actions
  setFiles: (files) => set({ files: files.map(f => File.fromJSON(f)) }),

  setCurrentFile: (file) => set({ currentFile: file ? File.fromJSON(file) : null }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error, isLoading: false }),

  clearError: () => set({ error: null }),

  setUploadProgress: (fileId, progress) => set(state => ({
    uploadProgress: { ...state.uploadProgress, [fileId]: progress }
  })),

  clearUploadProgress: (fileId) => set(state => {
    const newProgress = { ...state.uploadProgress };
    delete newProgress[fileId];
    return { uploadProgress: newProgress };
  }),

  // Fetch files
  fetchFiles: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fileApi.getFiles(params);
      set({ files: response.files.map(f => File.fromJSON(f)), isLoading: false });
      return { success: true, files: response.files };
    } catch (error) {
      set({ error: error.message, isLoading: false });
      return { success: false, error: error.message };
    }
  },

  // Upload file
  uploadFile: async (file, type = 'general', onProgress = null) => {
    const fileId = `temp_${Date.now()}`;
    set({ isLoading: true, error: null });
    
    if (onProgress) {
      set(state => ({
        uploadProgress: { ...state.uploadProgress, [fileId]: 0 }
      }));
    }

    try {
      const response = await fileApi.uploadFile(file, type);
      const newFile = File.fromJSON(response);
      
      set(state => ({
        files: [newFile, ...state.files],
        isLoading: false
      }));

      get().clearUploadProgress(fileId);
      return { success: true, file: newFile };
    } catch (error) {
      set({ error: error.message, isLoading: false });
      get().clearUploadProgress(fileId);
      return { success: false, error: error.message };
    }
  },

  // Delete file
  deleteFile: async (fileId) => {
    set({ isLoading: true, error: null });
    try {
      await fileApi.deleteFile(fileId);
      set(state => ({
        files: state.files.filter(f => f.id !== fileId),
        currentFile: state.currentFile?.id === fileId ? null : state.currentFile,
        isLoading: false
      }));
      return { success: true };
    } catch (error) {
      set({ error: error.message, isLoading: false });
      return { success: false, error: error.message };
    }
  },

  // Get file info
  getFileInfo: async (fileId) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fileApi.getFileInfo(fileId);
      const file = File.fromJSON(response);
      set({ currentFile: file, isLoading: false });
      return { success: true, file };
    } catch (error) {
      set({ error: error.message, isLoading: false });
      return { success: false, error: error.message };
    }
  },
}));

// File entity class
export class File {
  constructor(data = {}) {
    this.id = data.id || null;
    this.userId = data.user_id || data.userId || null;
    this.originalName = data.original_name || data.originalName || '';
    this.filename = data.filename || '';
    this.fileType = data.file_type || data.fileType || '';
    this.fileSize = data.file_size || data.fileSize || 0;
    this.mimeType = data.mime_type || data.mimeType || '';
    this.uploadType = data.upload_type || data.uploadType || 'general';
    this.processedData = data.processed_data || data.processedData || null;
    this.createdAt = data.created_at ? new Date(data.created_at) : null;
    this.url = data.url || null;
  }

  get displayName() {
    return this.originalName || this.filename;
  }

  get sizeFormatted() {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = this.fileSize;
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }

    return `${size.toFixed(1)} ${units[unitIndex]}`;
  }

  get extension() {
    return this.originalName.split('.').pop()?.toLowerCase() || '';
  }

  get isImage() {
    return this.mimeType?.startsWith('image/') || false;
  }

  get isDocument() {
    const docTypes = ['pdf', 'doc', 'docx', 'txt', 'md'];
    return docTypes.includes(this.extension) || this.mimeType?.includes('document');
  }

  get isArchive() {
    const archiveTypes = ['zip', 'rar', '7z', 'tar', 'gz'];
    return archiveTypes.includes(this.extension);
  }

  get typeIcon() {
    if (this.isImage) return '🖼️';
    if (this.isDocument) return '📄';
    if (this.isArchive) return '📦';
    if (this.extension === 'json') return '📋';
    return '📁';
  }

  isValid() {
    return this.id && this.originalName && this.fileSize > 0;
  }

  toJSON() {
    return {
      id: this.id,
      user_id: this.userId,
      original_name: this.originalName,
      filename: this.filename,
      file_type: this.fileType,
      file_size: this.fileSize,
      mime_type: this.mimeType,
      upload_type: this.uploadType,
      processed_data: this.processedData,
      created_at: this.createdAt?.toISOString(),
      url: this.url,
    };
  }

  static fromJSON(data) {
    return new File(data);
  }
}

// Utility functions
export const getFilesByType = (type) => {
  const { files } = useFileStore.getState();
  return files.filter(file => file.fileType === type);
};

export const getRecentFiles = (limit = 10) => {
  const { files } = useFileStore.getState();
  return files
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    .slice(0, limit);
};

export const searchFiles = (query) => {
  const { files } = useFileStore.getState();
  const lowercaseQuery = query.toLowerCase();
  return files.filter(file => 
    file.originalName.toLowerCase().includes(lowercaseQuery) ||
    file.fileType.toLowerCase().includes(lowercaseQuery)
  );
};

