/**
 * AuthContext.jsx — Estado global de autenticação.
 *
 * 🎓 O QUE é Context API?
 * No React, dados fluem "pra baixo" via props (pai → filho → neto).
 * Se o Neto precisar de dados do Avo, você teria que passar prop
 * por TODOS os componentes no caminho (prop drilling).
 *
 * Context API resolve isso: cria um "estado global" que QUALQUER
 * componente pode ler, sem prop drilling.
 *
 * Aqui guardamos: usuário logado + token JWT + funções login/logout.
 * Qualquer componente faz:  const { user, login } = useAuth()
 *
 * SOLID 'S': este arquivo SÓ cuida de autenticação (estado).
 * SOLID 'D': não depende de componentes, qualquer um consome.
 */
import { createContext, useContext, useState, useCallback } from 'react'
import { register as apiRegister, login as apiLogin } from '@/api/auth'

// createContext() cria o "canal" de comunicação.
// O valor padrão é null (será preenchido pelo Provider).
const AuthContext = createContext(null)

/**
 * AuthProvider — envolve o app e fornece dados de auth pra todos.
 * As children são TODOS os componentes dentro dele.
 */
export function AuthProvider({ children }) {
  // Estado: null = deslogado, objeto = logado
  const [user, setUser] = useState(() => {
    // Tenta recuperar sessão salva no localStorage (persistência)
    const saved = localStorage.getItem('finsmart_user')
    return saved ? JSON.parse(saved) : null
  })

  const [token, setToken] = useState(() =>
    localStorage.getItem('finsmart_token')
  )

  // loading evita "piscar" a tela de login antes de verificar sessão
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  /**
   * Função de login — chamada pelo formulário de login.
   * useCallback = memoriza a função (não recria a cada render).
   */
  const login = useCallback(async (email, password) => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiLogin({ email, password })
      // Salva token e dados do usuário
      localStorage.setItem('finsmart_token', data.access_token)
      localStorage.setItem('finsmart_user', JSON.stringify(data.user))
      setToken(data.access_token)
      setUser(data.user)
      return data.user
    } catch (err) {
      const msg = err.response?.data?.error || 'Erro ao fazer login'
      setError(msg)
      throw new Error(msg)
    } finally {
      setLoading(false)
    }
  }, [])

  /**
   * Função de cadastro.
   */
  const register = useCallback(async (name, email, password) => {
    setLoading(true)
    setError(null)
    try {
      await apiRegister({ name, email, password })
      // Após cadastro, faz login automático
      return await login(email, password)
    } catch (err) {
      const msg = err.response?.data?.error || 'Erro ao cadastrar'
      setError(msg)
      throw new Error(msg)
    } finally {
      setLoading(false)
    }
  }, [login])

  /**
   * Logout — limpa tudo e manda pra login.
   */
  const logout = useCallback(() => {
    localStorage.removeItem('finsmart_token')
    localStorage.removeItem('finsmart_user')
    setToken(null)
    setUser(null)
    setError(null)
  }, [])

  // Calculado: se tem token E user, está logado
  const isAuthenticated = !!token && !!user

  // Valor que todos os componentes recebem
  const value = {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

/**
 * Hook customizado — atalho para usar o contexto.
 * Em vez de importar useContext + AuthContext toda hora,
 * fazemos: const { user } = useAuth()
 */
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de <AuthProvider>')
  }
  return context
}
