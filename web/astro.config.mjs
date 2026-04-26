import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";

const repoBase = process.env.PAGES_BASE ?? "";

export default defineConfig({
  site: process.env.PAGES_SITE ?? "https://example.github.io",
  base: repoBase,
  output: "static",
  integrations: [tailwind()],
  markdown: {
    syntaxHighlight: "shiki",
    shikiConfig: { theme: "github-light" },
  },
});
