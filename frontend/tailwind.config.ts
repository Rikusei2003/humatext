import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--color-bg)",
        foreground: "var(--color-text)",
        muted: "var(--color-text-muted)",
        lighter: "var(--color-text-lighter)",
        primary: {
          DEFAULT: "var(--color-primary)",
          light: "var(--color-primary-light)",
        },
        surface: "var(--color-surface)",
        border: {
          DEFAULT: "var(--color-border)",
          light: "var(--color-border-light)",
        },
        polish: "var(--accent-polish)",
        enhance: "var(--accent-enhance)",
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
      },
      boxShadow: {
        card: "var(--shadow-card)",
        button: "var(--shadow-button)",
        featured: "var(--shadow-featured)",
      },
      fontFamily: {
        sans: ["-apple-system", "BlinkMacSystemFont", "'Segoe UI'", "sans-serif"],
        serif: ["Georgia", "'Noto Serif SC'", "serif"],
      },
    },
  },
  plugins: [],
};
export default config;
