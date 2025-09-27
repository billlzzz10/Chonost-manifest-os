import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
import { BundleAnalyzerPlugin } from 'webpack-bundle-analyzer'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    {
      name: 'bundle-analyzer',
      generateBundle() {
        // This will run the bundle analyzer after build
        const analyzer = new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
          reportFilename: 'bundle-report.html'
        })
      }
    }
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-button'],
          icons: ['lucide-react']
        }
      }
    }
  }
})