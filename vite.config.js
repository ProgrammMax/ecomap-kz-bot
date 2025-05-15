import { defineConfig } from 'vite' 
import vue from '@vitejs/plugin-vue'

export default defineConfig({   
  plugins: [vue()],
  server: {
    allowedHosts: [
      'ecomap-kz-bot.vercel.app'
    ],
    cors: {
      origin: '*'
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  }
}) 