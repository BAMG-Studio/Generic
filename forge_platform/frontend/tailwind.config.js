/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // We default to dark, but this allows toggling
  theme: {
    extend: {
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      colors: {
        // The "Void" Backgrounds - Deep, rich darks (not just black)
        canvas: {
          DEFAULT: '#0F172A', // Slate-900 (Main BG)
          panel: '#1E293B',   // Slate-800 (Widget BG)
          border: '#334155',  // Slate-700 (Borders)
          hover: '#2D3748',   // Slate-750 (Hover states)
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
      fontSize: {
        'xxs': '0.625rem',
      },
      boxShadow: {
        'neon': '0 0 10px theme("colors.brand.glow")',
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.3)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
