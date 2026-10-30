/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        brand: ['"Barlow Semi Condensed"', '"Arial Narrow"', 'sans-serif'],
        display: ['"Geist"', '"Plus Jakarta Sans"', 'ui-sans-serif', 'sans-serif'],
        sans: ['"Geist"', '"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
        mono: ['"Geist Mono"', 'ui-monospace', 'monospace'],
        hand: ['"Caveat"', '"Segoe Print"', 'cursive'],
        serif: ['"Instrument Serif"', 'ui-serif', 'Georgia', 'serif'],
      },
      colors: {
        ink: {
          DEFAULT: '#0b0f19',
          50: '#f8fafc',
          100: '#f1f5f9',
          500: '#64748b',
          900: '#0b0f19',
        },
        pinkdeep: '#ec4899',
        bluedeep: '#2563eb',
        mintdeep: '#059669',
        mint: '#10b981',
        sundeep: '#d97706',
        butter: '#fef3c7',
        lavender: '#ede9fe',
        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        }
      }
    },
  },
  plugins: [],
}
