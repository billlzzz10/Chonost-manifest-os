import { useState } from 'react';

const MCP_SERVER_URL = import.meta.env.VITE_MCP_SERVER_URL || 'http://localhost:3001';

export type LogEntry = {
  phase: string;
  tool: string;
  status: string;
  latency_ms: number;
};

export type ApiResponse<T = unknown> = {
  result: T;
};

export type ApiError = {
  error: string;
  details?: string;
};

// Log performance metrics
export const logRun = (logEntry: LogEntry): void => {
  fetch(`${MCP_SERVER_URL}/runlog/put`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(logEntry),
  }).catch(console.error); // Fire-and-forget logging
};

// Generic API call hook
export const useApiCall = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const callApi = async <T = unknown>(
    endpoint: string,
    body: Record<string, unknown>,
    toolName: string
  ): Promise<T | null> => {
    setIsLoading(true);
    setError(null);

    const startTime = Date.now();

    try {
      const response = await fetch(`${MCP_SERVER_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data: ApiResponse<T> | ApiError = await response.json();
      const latency_ms = Date.now() - startTime;

      if (!response.ok) {
        const errorData = data as ApiError;
        const errorMessage = errorData.error || 'API call failed';
        logRun({ phase: 'error', tool: toolName, status: 'failed', latency_ms });
        throw new Error(errorMessage);
      }

      logRun({ phase: 'tool', tool: toolName, status: 'success', latency_ms });
      return (data as ApiResponse<T>).result;
    } catch (error) {
      const latency_ms = Date.now() - startTime;
      logRun({ phase: 'error', tool: toolName, status: 'failed', latency_ms });

      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  return { callApi, isLoading, error };
};