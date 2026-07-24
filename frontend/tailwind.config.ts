import type { Config } from "tailwindcss";

// Design tokens map to the system defined in docs/frontend/04-design-system.MD.
const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        // Brand palette. White dominates the layout; navy is the ink/primary,
        // gold the accent, and `ink` (darker navy) fills emphasis cards/sections.
        navy: "#12233F",
        ink: "#0D1B32",
        gold: "#C9A84C",
      },
    },
  },
  plugins: [],
};

export default config;
