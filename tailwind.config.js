/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/input.css"
  ],
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
                        'card-border': '#f3f4f6'
                    },
                    fontFamily: {
                        'oswald': ['Oswald', 'sans-serif'],
                        'bebas-neue': ['Bebas Neue', 'sans-serif'],
                    }
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
  ],
}
