/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          blue: '#7ec8e3',
          dark: '#0f3460',
          darker: '#1a1a2e',
          panel: '#16213e',
          card: '#1e2a3a',
          border: '#2a2a4a',
        }
      }
    },
  },
  plugins: [],
}

