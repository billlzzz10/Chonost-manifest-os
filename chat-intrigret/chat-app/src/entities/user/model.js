/**
 * User Entity Model
 * 
 * This module defines the User entity and related operations.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import apiClient, { authApi } from '../../shared/api/client';

// User store using Zustand
export const useUserStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      setUser: (user) => {
        set({ user, isAuthenticated: !!user, error: null });
        if (user?.token) {
          apiClient.setToken(user.token);
        }
      },

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error, isLoading: false }),

      clearError: () => set({ error: null }),

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login(credentials);
          const user = response.user;
          user.token = response.token;
          
          get().setUser(user);
          return { success: true, user };
        } catch (error) {
          set({ error: error.message, isLoading: false });
          return { success: false, error: error.message };
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.register(userData);
          const user = response.user;
          user.token = response.token;
          
          get().setUser(user);
          return { success: true, user };
        } catch (error) {
          set({ error: error.message, isLoading: false });
          return { success: false, error: error.message };
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          await authApi.logout();
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          set({ user: null, isAuthenticated: false, isLoading: false, error: null });
          apiClient.setToken(null);
        }
      },

      refreshToken: async () => {
        try {
          const response = await authApi.refreshToken();
          const user = get().user;
          if (user) {
            user.token = response.token;
            get().setUser(user);
          }
          return { success: true };
        } catch (error) {
          get().logout();
          return { success: false, error: error.message };
        }
      },

      // Initialize authentication state
      initialize: () => {
        const { user } = get();
        if (user?.token) {
          apiClient.setToken(user.token);
          set({ isAuthenticated: true });
        }
      },
    }),
    {
      name: 'user-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// User entity class
export class User {
  constructor(data = {}) {
    this.id = data.id || null;
    this.username = data.username || '';
    this.email = data.email || '';
    this.createdAt = data.created_at ? new Date(data.created_at) : null;
    this.updatedAt = data.updated_at ? new Date(data.updated_at) : null;
    this.token = data.token || null;
  }

  get displayName() {
    return this.username || this.email;
  }

  get initials() {
    if (this.username) {
      return this.username
        .split(' ')
        .map(name => name[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
    }
    return this.email[0].toUpperCase();
  }

  isValid() {
    return this.id && this.email && this.username;
  }

  toJSON() {
    return {
      id: this.id,
      username: this.username,
      email: this.email,
      created_at: this.createdAt?.toISOString(),
      updated_at: this.updatedAt?.toISOString(),
    };
  }

  static fromJSON(data) {
    return new User(data);
  }
}

// Utility functions
export const getCurrentUser = () => {
  const { user } = useUserStore.getState();
  return user ? User.fromJSON(user) : null;
};

export const isAuthenticated = () => {
  const { isAuthenticated } = useUserStore.getState();
  return isAuthenticated;
};

export const requireAuth = () => {
  if (!isAuthenticated()) {
    throw new Error('Authentication required');
  }
  return getCurrentUser();
};

