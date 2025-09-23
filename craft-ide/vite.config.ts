import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // Prevent Vite from clearing the screen
  clearScreen: false,
  // Tauri expects a fixed port, fail if that port is not available
  server: {
    port: 5173,
    strictPort: true,
  },
  // Enable environment variables
  // https://vitejs.dev/guide/env-and-mode.html
  envPrefix: ["VITE_", "TAURI_"],
  // Optimize bundle size and load time via code-splitting
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          react: ["react", "react-dom"],
          mermaid: ["mermaid"],
          monaco: ["monaco-editor", "@monaco-editor/react"],
          chart: ["chart.js", "react-chartjs-2"],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  optimizeDeps: {
    include: ["react", "react-dom"],
    exclude: ["mermaid", "monaco-editor"],
  },
});
