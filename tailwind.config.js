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
                        'mint': '#6ee7b7', // Примерный цвет для mint
                        'green': {
                            400: '#4ade80',
                            900: '#14532d'
                        },
                    },
                    fontFamily: {
                        'lilita': ['Lilita One', 'cursive'],
                        'arvo': ['Arvo', 'serif'],
                    }
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
  ],
}
