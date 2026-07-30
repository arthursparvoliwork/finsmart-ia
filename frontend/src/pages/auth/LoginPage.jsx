/**
 * LoginPage.jsx — Tela de login/cadastro.
 *
 * 🎓 Framer Motion: lib de animações React-first.
 * - motion.div = div que pode ser animada
 * - initial = estado inicial (de onde vem)
 * - animate = estado final (onde vai)
 * - transition = como faz a transição
 *
 * Aqui usamos um "fade up" (sobe e aparece) na entrada.
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '@/contexts/AuthContext'

// Variações de animação reutilizáveis
const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5, ease: 'easeOut' },
}

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false) // alterna login/cadastro
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  })
  const [localError, setLocalError] = useState('')

  const { login, register, error, loading } = useAuth()
  const navigate = useNavigate()

  function handleChange(e) {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLocalError('')
    try {
      if (isRegister) {
        await register(formData.name, formData.email, formData.password)
      } else {
        await login(formData.email, formData.password)
      }
      navigate('/dashboard') // login sucesso → vai pro dashboard
    } catch {
      setLocalError(error || 'Erro ao processar')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-brand-50 via-white to-brand-100">
      <motion.div
        className="w-full max-w-md mx-4"
        {...fadeInUp}
      >
        {/* Logo/Título */}
        <div className="text-center mb-8">
          <motion.h1
            className="text-4xl font-bold text-brand-700"
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, type: 'spring' }}
          >
            🏦 FinSmart IA
          </motion.h1>
          <p className="text-slate-500 mt-2">
            {isRegister
              ? 'Crie sua conta e comece a analisar suas finanças'
              : 'Faça login para acessar seu dashboard'}
          </p>
        </div>

        {/* Card do formulário */}
        <motion.div
          className="bg-white rounded-2xl shadow-lg p-8 border border-slate-100"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          {/* Mensagem de erro */}
          {(localError || error) && (
            <motion.div
              className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
            >
              {localError || error}
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Campo Nome (só no cadastro) */}
            {isRegister && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
              >
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Nome completo
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  minLength={2}
                  className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none transition-all text-slate-800 placeholder-slate-400"
                  placeholder="Seu nome"
                />
              </motion.div>
            )}

            {/* Campo Email */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none transition-all text-slate-800 placeholder-slate-400"
                placeholder="seu@email.com"
              />
            </div>

            {/* Campo Senha */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Senha
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={6}
                className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none transition-all text-slate-800 placeholder-slate-400"
                placeholder="Mínimo 6 caracteres"
              />
            </div>

            {/* Botão Submit */}
            <motion.button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {loading
                ? '⏳ Processando...'
                : isRegister
                  ? 'Criar Conta'
                  : 'Entrar'}
            </motion.button>
          </form>

          {/* Toggle login/cadastro */}
          <div className="mt-6 text-center text-sm text-slate-500">
            {isRegister ? (
              <p>
                Já tem conta?{' '}
                <button
                  onClick={() => setIsRegister(false)}
                  className="text-brand-600 font-semibold hover:text-brand-700"
                >
                  Faça login
                </button>
              </p>
            ) : (
              <p>
                Não tem conta?{' '}
                <button
                  onClick={() => setIsRegister(true)}
                  className="text-brand-600 font-semibold hover:text-brand-700"
                >
                  Cadastre-se grátis
                </button>
              </p>
            )}
          </div>
        </motion.div>

        {/* Footer */}
        <p className="text-center text-xs text-slate-400 mt-6">
          FinSmart IA © 2026 — Projeto portfólio
        </p>
      </motion.div>
    </div>
  )
}
