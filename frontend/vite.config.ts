import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    allowedHosts: [
      '.ngrok-free.dev',
      '.ngrok.io',
      '.ngrok.app',
      'localhost',
    ],
    hmr: {
      overlay: false,
    },
    proxy: {
      // Proxy API requests to backend
      '/vision': 'http://localhost:8000',
      '/brain': 'http://localhost:8000',
      '/speech': 'http://localhost:8000',
      '/command': 'http://localhost:8000',
      '/navigation': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
