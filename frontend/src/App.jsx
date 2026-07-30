/**
 * App.jsx — Componente raiz do React.
 *
 * Rotas:
 *   /login         → tela de login/cadastro
 *   /dashboard     → dashboard (protegido)
 *   /transactions  → transações + IA (protegido)
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/contexts/AuthContext'
import ProtectedRoute from '@/components/layout/ProtectedRoute'
import LoginPage from '@/pages/auth/LoginPage'
import DashboardPage from '@/pages/dashboard/DashboardPage'
import TransactionsPage from '@/pages/transactions/TransactionsPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Rotas públicas */}
          <Route path="/login" element={<LoginPage />} />

          {/* Rotas protegidas (exigem login) */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/transactions"
            element={
              <ProtectedRoute>
                <TransactionsPage />
              </ProtectedRoute>
            }
          />

          {/* Rota padrão: redireciona */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* 404 */}
          <Route path="*" element={
            <div className="min-h-screen flex items-center justify-center">
              <div className="text-center">
                <h1 className="text-6xl font-bold text-brand-600">404</h1>
                <p className="text-slate-500 mt-2">Página não encontrada</p>
                <a href="/dashboard" className="text-brand-600 hover:underline mt-4 inline-block">
                  Voltar ao dashboard
                </a>
              </div>
              </div>
          } />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
