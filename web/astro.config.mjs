import { defineConfig } from "astro/config";

export default defineConfig({
  site: process.env.PAGES_SITE ?? "https://example.github.io",
  base: process.env.PAGES_BASE ?? "",
  output: "static",
  markdown: {
    syntaxHighlight: "shiki",
    shikiConfig: { theme: "github-light" },
  },
});
