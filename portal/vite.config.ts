import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

const repositoryRoot = fileURLToPath(new URL("..", import.meta.url));

export default defineConfig({
  base: "/ai-setup/",
  plugins: [react(), tailwindcss()],
  server: {
    fs: { allow: [repositoryRoot] },
  },
});
