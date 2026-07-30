import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// Configuração do Vite
// - react(): habilita JSX e Fast Refresh (hot reload)
// - tailwindcss(): plugin do Tailwind v4 (NÃO precisa de tailwind.config.js)
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      // '@' vira atalho para /src. Em vez de '../../components/Button',
      // você escreve '@/components/Button'. Padrão da comunidade React.
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    // Proxy: requisições /api vão pro backend Flask (porta 5000).
    // Assim evitamos problemas de CORS em desenvolvimento.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
})
