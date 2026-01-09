import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // NOiSEMaKER Brand Colors
        'nm-dark-blue': '#0a1569',
        'nm-purple': '#2f10b7',
        'nm-cyan': '#00e4ff',
        'nm-magenta': '#d824d3',
        'nm-pink-light': '#fdf2fc',
        'nm-blue-light': '#73a8ff',
        'nm-black': '#0C0D0D',
      },
      fontFamily: {
        anisette: ['Anisette STD Bold', 'sans-serif'],
        bebas: ['Bebas Neue', 'Impact', 'sans-serif'],
        cormorant: ['Cormorant Garamond', 'Georgia', 'serif'],
        space: ['Space Grotesk', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

export default config
