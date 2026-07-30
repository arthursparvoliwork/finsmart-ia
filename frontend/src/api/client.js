/**
 * client.js — Cliente HTTP central (Axios).
 *
 * Por que centralizar?
 * - Em vez de cada componente criar seu próprio axios.get(...),
 *   todos importam este 'api'. Configuração num lugar só.
 * - Interceptor adiciona o token JWT automaticamente em TODA requisição.
 *   O componente não precisa se preocupar com isso.
 *
 * Princípio SOLID 'S' (Single Responsibility):
 * - Este arquivo SÓ sabe fazer requisições HTTP.
 */
import axios from 'axios'

// Cria uma instância do axios com configuração base.
// baseURL = todas as URLs começam com /api (o proxy do Vite encaminha pro Flask).
const api = axios.create({
  baseURL: '/api',
  timeout: 10000, // 10 segundos — evita ficar travado se a API morrer
  headers: {
    'Content-Type': 'application/json',
  },
})

// =====================================================
// INTERCEPTOR DE REQUISIÇÃO: adiciona token JWT
// =====================================================
// Toda vez que uma requisição sai, este código roda ANTES.
// Ele busca o token no localStorage e coloca no header Authorization.
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('finsmart_token')
    if (token) {
      // Padrão HTTP: "Authorization: Bearer <token>"
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// =====================================================
// INTERCEPTOR DE RESPOSTA: trata erros globalmente
// =====================================================
// Se a API retornar 401 (token inválido/expirado), desloga o usuário.
api.interceptors.response.use(
  (response) => response, // sucesso: passa direto
  (error) => {
    if (error.response?.status === 401) {
      // Token inválido ou expirado — limpa e manda pro login
      localStorage.removeItem('finsmart_token')
      localStorage.removeItem('finsmart_user')
      // Só redireciona se NÃO estiver já na página de login
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
