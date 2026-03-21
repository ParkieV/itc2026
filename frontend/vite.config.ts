import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';


export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  optimizeDeps: {
    esbuildOptions: {
      define: {
        global: 'globalThis'
      },
    }
  }, 
  build: {
    
  },
  server: {
    watch: {
      usePolling: true,
    },
    host: true,
    strictPort: true,
    port: 8000,
  },
  preview: {
    host: true,
    strictPort: true,
    port: 8080,
  },
});
