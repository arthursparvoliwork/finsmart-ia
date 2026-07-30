/**
 * ProtectedRoute.jsx — Protege rotas que exigem login.
 *
 * 🎓 O QUE faz:
 * Se o usuário NÃO está logado, redireciona pra /login.
 * Se está logado, renderiza a página normalmente.
 *
 * 🎓 POR QUÊ separar num componente?
 * Em vez de colocar lógica de "está logado?" dentro de cada página,
 * centralizamos aqui. É o padrão "Guard" do React Router.
 */
import { Navigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()

  // Enquanto verifica sessão (localStorage), mostra nada (evita flash)
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <div className="text-brand-600 font-semibold text-lg">Carregando...</div>
      </div>
    )
  }

  // Não logado? Manda pro login (preserve a URL pra voltar depois)
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Logado? Renderiza a página
  return children
}
