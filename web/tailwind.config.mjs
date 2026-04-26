/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,ts,md}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        accent: "#2563eb",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
      },
    },
  },
};
