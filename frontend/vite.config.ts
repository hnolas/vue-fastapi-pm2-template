import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path
      }
    },
    fs: {
      // Allow serving files from one level up to the project root
      allow: ['..']
    },
    hmr: {
      // Disable host check for HMR to work on Replit
      host: 'localhost'
    },
    // Allow all hosts
    cors: true,
    // Allow specific Replit hosts
    allowedHosts: [
      'localhost',
      '*.replit.dev',
      '*.repl.co',
      '*.replit.app',
      'ef452fb6-087a-4e67-8c69-d5f401232edb-00-3i40lm8z4g9ib.riker.replit.dev'
    ]
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
