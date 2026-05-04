/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // SafeLab palette — clinical green + amber accent + warm paper.
        // Kept under the `biolab` namespace so existing utility classes
        // (text-biolab-700, bg-biolab-50, etc.) automatically pick up the
        // new tones without touching every file.
        biolab: {
          50:  "#f4f1ea",  // paper (background)
          100: "#ebe6da",  // paper-2
          200: "#d8d2c2",  // line / hairline
          300: "#c8e6dd",  // mint trace (brand-3)
          400: "#5a9389",  // mid-tone (used for borders/hovers)
          500: "#0f5d4d",  // brand (primary)
          600: "#0c4f41",
          700: "#0a3d33",  // brand-2 (deep forest)
          800: "#0a3329",
          900: "#0e1a16",  // ink
        },
        // SafeLab semantic tokens (also exposed for direct use).
        safelab: {
          paper:   "#f4f1ea",
          paper2:  "#ebe6da",
          line:    "#d8d2c2",
          ink:     "#0e1a16",
          ink2:    "#1a2a23",
          brand:   "#0f5d4d",
          brand2:  "#0a3d33",
          brand3:  "#c8e6dd",
          accent:  "#d4a24a",
        },
        risk: {
          safe:   "#2f7d63",  // SafeLab risk-low
          unknown:"#d4a24a",  // SafeLab risk-mid (amber)
          unsafe: "#b8442e",  // SafeLab risk-high
        },
      },
      fontFamily: {
        sans:    ["Space Grotesk", "Inter", "system-ui", "sans-serif"],
        display: ["Space Grotesk", "Inter", "sans-serif"],
        serif:   ["Instrument Serif", "Georgia", "serif"],
        mono:    ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        // Tighter, technical-feeling shadows.
        soft:  "0 1px 2px rgba(14,26,22,0.04), 0 4px 16px rgba(14,26,22,0.05)",
        card:  "0 1px 3px rgba(14,26,22,0.06), 0 4px 16px rgba(14,26,22,0.04)",
      },
      borderRadius: {
        // Override Tailwind defaults so `rounded-xl/2xl` already used in the
        // codebase resolves to crisp/technical corners (per SafeLab spec).
        DEFAULT: "2px",
        sm:      "2px",
        md:      "3px",
        lg:      "4px",
        xl:      "4px",
        "2xl":   "6px",
        "3xl":   "8px",
        full:    "9999px",
      },
      backgroundImage: {
        // Faint technical grid for backgrounds (used on body via .bg-biolab-pattern).
        "grid-paper":
          "linear-gradient(to right, rgba(14,26,22,0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(14,26,22,0.04) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};
