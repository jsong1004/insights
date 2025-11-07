import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  // Root directory for source files
  root: resolve(__dirname, 'static/src'),

  // Base public path
  base: '/static/dist/',

  // Build configuration
  build: {
    // Output directory relative to project root
    outDir: resolve(__dirname, 'static/dist'),
    emptyOutDir: true,

    // Generate manifest for Flask integration
    manifest: true,

    // Rollup options
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'static/src/ts/main.ts'),
        styles: resolve(__dirname, 'static/src/css/main.css'),
      },
      output: {
        entryFileNames: 'js/[name].[hash].js',
        chunkFileNames: 'js/[name].[hash].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name?.endsWith('.css')) {
            return 'css/[name].[hash][extname]';
          }
          return 'assets/[name].[hash][extname]';
        },
      },
    },

    // Source maps for development
    sourcemap: true,

    // Minification
    minify: 'esbuild',

    // Target modern browsers
    target: 'es2020',
  },

  // Development server configuration
  server: {
    port: 3000,
    strictPort: true,
    cors: true,

    // Increase header size limit to prevent 431 errors
    maxHeaderSize: 16384, // 16KB (default is 8KB)

    // Proxy API requests to Flask development server
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        // Remove problematic headers
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            // Remove large cookie headers if they exceed limits
            const cookie = proxyReq.getHeader('cookie');
            if (cookie && cookie.toString().length > 8000) {
              console.warn('[Vite] Large cookie header detected, consider clearing cookies');
            }
          });
        },
      },
      '/auth': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
    },
  },

  // CSS options
  css: {
    devSourcemap: true,
  },

  // Resolve options
  resolve: {
    alias: {
      '@': resolve(__dirname, 'static/src'),
      '@ts': resolve(__dirname, 'static/src/ts'),
      '@css': resolve(__dirname, 'static/src/css'),
    },
  },

  // Clear console on rebuild
  clearScreen: false,
});
