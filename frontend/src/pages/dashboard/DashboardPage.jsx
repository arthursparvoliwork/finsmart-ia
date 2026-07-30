/**
 * DashboardPage.jsx — Página principal do dashboard (CONECTADA À API REAL).
 *
 * 🎓 DIFERENÇA vs versão anterior:
 * Agora busca dados REAIS do backend via getSummary() e listTransactions().
 * Os cards e gráficos refletem as transações reais do usuário.
 */
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts'
import { useAuth } from '@/contexts/AuthContext'
import { getSummary, listTransactions } from '@/api/transactions'

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
}
const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
}

function SummaryCard({ title, value, icon, color }) {
  return (
    <motion.div
      variants={cardVariants}
      className="bg-white rounded-xl shadow-sm border border-slate-100 p-6 hover:shadow-md transition-shadow"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500 font-medium">{title}</p>
          <p className="text-2xl font-bold text-slate-800 mt-1">{value}</p>
        </div>
        <div className={`w-12 h-12 rounded-full ${color} flex items-center justify-center text-2xl`}>
          {icon}
        </div>
      </div>
    </motion.div>
  )
}

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const [resumo, setResumo] = useState({
    total_receitas: 0, total_despesas: 0, saldo: 0
  })
  const [grafico, setGrafico] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function carregar() {
      try {
        const [s, transacoes] = await Promise.all([getSummary(), listTransactions()])
        setResumo(s)

        // Agrupa por mês pra fazer o gráfico
        const porMes = {}
        transacoes.forEach((t) => {
          const mes = new Date(t.data).toLocaleDateString('pt-BR', { month: 'short' })
          if (!porMes[mes]) porMes[mes] = { mes, receitas: 0, despesas: 0 }
          if (t.tipo === 'receita') porMes[mes].receitas += parseFloat(t.valor)
          else porMes[mes].despesas += parseFloat(t.valor)
        })
        setGrafico(Object.values(porMes))
      } catch (e) {
        // silencioso: dados começam vazios
      } finally {
        setLoading(false)
      }
    }
    carregar()
  }, [])

  function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency', currency: 'BRL'
    }).format(value)
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navbar */}
      <motion.nav
        className="bg-white border-b border-slate-100 px-6 py-4 flex items-center justify-between sticky top-0 z-10"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">🏦</span>
          <h1 className="text-xl font-bold text-brand-700">FinSmart IA</h1>
        </div>
        <div className="flex items-center gap-4">
          <a href="/transactions" className="text-sm text-brand-600 hover:text-brand-700 font-medium">
            Transações
          </a>
          <span className="text-sm text-slate-600">
            Olá, <strong>{user?.name}</strong>
          </span>
          <motion.button
            onClick={logout}
            className="text-sm text-slate-500 hover:text-red-500 transition-colors px-3 py-1 rounded-lg hover:bg-red-50"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Sair
          </motion.button>
        </div>
      </motion.nav>

      {/* Conteúdo */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <motion.h2
          className="text-2xl font-bold text-slate-800 mb-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          📊 Dashboard
        </motion.h2>

        {/* Cards */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <SummaryCard title="Total Receitas" value={formatCurrency(resumo.total_receitas)} icon="📈" color="bg-emerald-100" />
          <SummaryCard title="Total Despesas" value={formatCurrency(resumo.total_despesas)} icon="📉" color="bg-red-100" />
          <SummaryCard title="Saldo" value={formatCurrency(resumo.saldo)} icon="💰" color="bg-brand-100" />
        </motion.div>

        {/* Gráfico */}
        <motion.div
          className="bg-white rounded-xl shadow-sm border border-slate-100 p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          <h3 className="text-lg font-semibold text-slate-700 mb-4">
            Receitas vs Despesas
          </h3>
          {loading ? (
            <p className="text-slate-400 text-center py-8">Carregando gráfico...</p>
          ) : grafico.length === 0 ? (
            <p className="text-slate-400 text-center py-8">
              Adicione transações para ver o gráfico.
              <a href="/transactions" className="text-brand-600 hover:underline ml-1">Adicionar →</a>
            </p>
          ) : (
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={grafico}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="mes" tick={{ fontSize: 13, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 13, fill: '#64748b' }} tickFormatter={(v) => `R$${(v / 1000).toFixed(0)}k`} />
                <Tooltip formatter={(value) => formatCurrency(value)} contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }} />
                <Legend />
                <Bar dataKey="receitas" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Receitas" />
                <Bar dataKey="despesas" fill="#ef4444" radius={[4, 4, 0, 0]} name="Despesas" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </motion.div>

        {/* Próximos passos */}
        <motion.div
          className="mt-8 bg-brand-50 rounded-xl border border-brand-100 p-6 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <p className="text-brand-700 font-medium">
            🚀 Em breve: chat com IA (LangChain), detecção de anomalias (TensorFlow) e visual 3D (Three.js + GSAP)!
          </p>
        </motion.div>
      </main>
    </div>
  )
}
