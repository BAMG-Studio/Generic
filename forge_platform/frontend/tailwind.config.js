/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // We default to dark, but this allows toggling
  theme: {
    extend: {
      colors: {
        // The "Void" Backgrounds - Deep, rich darks (not just black)
        canvas: {
          DEFAULT: '#0F172A', // Slate-900 (Main BG)
          panel: '#1E293B',   // Slate-800 (Widget BG)
          border: '#334155',  // Slate-700 (Borders)
        },
        
        // The "Intelligence" Accent - Primary Brand Color
        brand: {
          light: '#818CF8', // Indigo-400
          DEFAULT: '#6366F1', // Indigo-500
          dark: '#4338CA',  // Indigo-700
          glow: 'rgba(99, 102, 241, 0.5)', // For shadows/glows
        },

        // IP Classification Colors (The "Traffic Light" system)
        ip: {
          foreground: {
            DEFAULT: '#10B981', // Emerald-500 (Your Code)
            dim: 'rgba(16, 185, 129, 0.1)',
          },
          thirdParty: {
            DEFAULT: '#F59E0B', // Amber-500 (Open Source)
            dim: 'rgba(245, 158, 11, 0.1)',
          },
          background: {
            DEFAULT: '#64748B', // Slate-500 (Vendor/Legacy)
            dim: 'rgba(100, 116, 139, 0.1)',
          },
          risk: {
            DEFAULT: '#EF4444', // Red-500 (High Risk/GPL)
            dim: 'rgba(239, 68, 68, 0.1)',
          }
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'], // Crucial for the code viewer
      },
      boxShadow: {
        'neon': '0 0 10px theme("colors.brand.glow")',
      }
    },
  },
  plugins: [],
}
