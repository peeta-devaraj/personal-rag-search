/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "-apple-system", "Segoe UI", "sans-serif"],
      },
      colors: {
        base: {
          950: "#08090c",
          900: "#0d0f14",
          800: "#14161d",
          700: "#1c1f29",
          600: "#262a37",
        },
      },
      backgroundImage: {
        "brand-gradient": "linear-gradient(135deg, #818cf8 0%, #a78bfa 50%, #f472b6 100%)",
        "brand-gradient-soft": "linear-gradient(135deg, rgba(129,140,248,0.15) 0%, rgba(167,139,250,0.15) 50%, rgba(244,114,182,0.15) 100%)",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(129,140,248,0.15), 0 8px 24px -8px rgba(129,140,248,0.35)",
        card: "0 1px 0 0 rgba(255,255,255,0.03) inset, 0 8px 24px -12px rgba(0,0,0,0.5)",
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "pulse-dot": {
          "0%, 100%": { opacity: "0.3" },
          "50%": { opacity: "1" },
        },
      },
      animation: {
        shimmer: "shimmer 2s linear infinite",
        "pulse-dot": "pulse-dot 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
