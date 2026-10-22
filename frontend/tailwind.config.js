/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        rose: {
          50: '#fff1f2',
          100: '#ffe4e6',
          200: '#fecdd3',
          300: '#fda4af',
          400: '#fb7185',
          500: '#f43f5e',
          600: '#e11d48',
          700: '#be123c',
          800: '#9f1239',
          900: '#881337',
          950: '#4c0519',
        },
        crimson: {
          50: '#fff0f2',
          100: '#ffe1e5',
          200: '#ffc8cf',
          500: '#e11d48',
          600: '#be123c',
          700: '#9f1239',
        },
        coral: {
          50: '#fff5f5',
          100: '#fed7d7',
          500: '#f56565',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'rose': '0 4px 14px 0 rgba(225, 29, 72, 0.15)',
        'rose-lg': '0 10px 25px -3px rgba(225, 29, 72, 0.2)',
      }
    },
  },
  plugins: [],
}
