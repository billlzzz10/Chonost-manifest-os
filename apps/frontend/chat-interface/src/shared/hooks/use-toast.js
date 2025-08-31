import { useState, useCallback } from 'react';

// Simple toast implementation
export const useToast = () => {
  const [toasts, setToasts] = useState([]);

  const toast = useCallback(({ title, description, variant = 'default' }) => {
    const id = Date.now();
    const newToast = {
      id,
      title,
      description,
      variant
    };

    setToasts(prev => [...prev, newToast]);

    // Auto remove after 5 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);

    // For now, just use browser alert as fallback
    if (variant === 'destructive') {
      alert(`Error: ${title}\n${description}`);
    } else {
      console.log(`Toast: ${title} - ${description}`);
    }
  }, []);

  const dismiss = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return {
    toast,
    dismiss,
    toasts
  };
};

