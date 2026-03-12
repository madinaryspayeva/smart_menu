/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/input.css"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'pastel-pink': '#ff9a8b',
        'pastel-yellow': '#fef9e7',
        'coral-red': '#d44f4f',
        'light-pink': '#fff5f5',
        'lemon': '#fef08a',
        'lemon-dark': '#facc15',
        'lemon-light': '#fef9c3',
        'lemon-border': '#eab308',
        'mint': '#6ee7b7', 
        'green': {
          400: '#4ade80',
          900: '#14532d'
        },
        'dark-gray': '#374151',
        'soft-white': '#fafafa',
        'card-border': '#f3f4f6',
        'dark-bg': '#1A1C24',
        'dark-secondary': '#252833',
        'dark-border': '#3A3E4C',
        'dark-text': '#A0A4B3',
        'orange-main': '#FF8811',
        'orange-dark': '#E98C00',
        'orange-light': '#FFDA9D',
        'gold-main': '#FFBB37',
        'gold-lightest': '#FEFCF5',
        'text-black': '#313449',
        'text-gray': '#6B6E81',
        'border-tan': '#F0ECE2',
      },
      fontFamily: {
        'oswald': ['Oswald', 'sans-serif'],
        'bebas-neue': ['Bebas Neue', 'sans-serif'],
        'cupidus': ['Cupidus', 'sans-serif'],
        'inter': ['Inter', 'sans-serif'],
      },
      backgroundImage: {
        'hero-pattern': "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0 L60 30 L30 60 L0 30 Z' fill='%23FFDA9D' opacity='0.15'/%3E%3C/svg%3E\")",
        'gradient-orange': 'linear-gradient(135deg, #FF8811, #FFBB37)',
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.8s ease',
        'scale-in': 'scaleIn 0.8s ease',
        'slide-left': 'slideInLeft 0.3s ease',
        'pulse-slow': 'pulse 2s infinite',
        'rotate-slow': 'rotate 0.5s ease',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-50px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        pulse: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' },
        },
        rotate: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
    },
  },
  plugins: [],
}