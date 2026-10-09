import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dev server forwards API calls to Flask, so the browser needs no CORS setup.
const target = process.env.API_PROXY_TARGET || "http://127.0.0.1:5000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": target,
      "/health": target,
    },
  },
});
