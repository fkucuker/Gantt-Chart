// /frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Nunito', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        // Custom semantic colors for the app
        surface: {
          light: '#ffffff',
          dark: '#1e293b', // slate-800
        },
        background: {
          light: '#f8fafc', // slate-50
          dark: '#0f172a', // slate-900
        }
      }
    },
  },
  plugins: [],
}

