import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  site: process.env.PAGES_SITE ?? "https://example.github.io",
  base: process.env.PAGES_BASE ?? "",
  output: "static",
  vite: {
    plugins: [tailwindcss()],
  },
  markdown: {
    syntaxHighlight: "shiki",
    shikiConfig: { theme: "github-light" },
  },
});
