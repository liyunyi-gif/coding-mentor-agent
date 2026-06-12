/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gpt: {
          sidebar: '#f9fafb',
          hover: '#f3f4f6',
          user: '#eff6ff',
          border: '#e5e7eb',
        }
      }
    },
  },
  plugins: [],
}

