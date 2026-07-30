/**
 * DashboardPage.jsx — Página principal do dashboard.
 *
 * 🎓 O que mostra:
 * - Cards de resumo (total receitas, despesas, saldo)
 * - Gráfico de barras (gastos por mês) com Recharts
 * - Animações de entrada com Framer Motion (staggered = uma após outra)
 *
 * 🎓 Framer Motion 'stagger':
 * Cada card aparece com um pequeno atraso (0.1s entre eles),
 * criando efeito "cascata". Muito mais profissional que tudo de uma vez.
 */
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts'
import { useAuth } from '@/contexts/AuthContext'

// Dados mock (vamos conectar com a API real na Fase 2b)
const DADOS_GRAFICO = [
  { mes: 'Jan', receitas: 5200, despesas: 3800 },
  { mes: 'Fev', receitas: 5800, despesas: 4100 },
  { mes: 'Mar', receitas: 4900, despesas: 3600 },
  { mes: 'Abr', receitas: 6100, despesas: 4500 },
  { mes: 'Mai', receitas: 5500, despesas: 3900 },
  { mes: 'Jun', receitas: 6400, despesas: 4200 },
]

// Animação staggered: cada filho aparece com delay crescente
const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.1, // 0.1s entre cada card
    },
  },
}

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
}

// Cards de resumo
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

  // Calcula totais (mock)
  const totalReceitas = DADOS_GRAFICO.reduce((s, d) => s + d.receitas, 0)
  const totalDespesas = DADOS_GRAFICO.reduce((s, d) => s + d.despesas, 0)
  const saldo = totalReceitas - totalDespesas

  function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
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

        {/* Cards de resumo (staggered) */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <SummaryCard
            title="Total Receitas"
            value={formatCurrency(totalReceitas)}
            icon="📈"
            color="bg-emerald-100"
          />
          <SummaryCard
            title="Total Despesas"
            value={formatCurrency(totalDespesas)}
            icon="📉"
            color="bg-red-100"
          />
          <SummaryCard
            title="Saldo"
            value={formatCurrency(saldo)}
            icon="💰"
            color="bg-brand-100"
          />
        </motion.div>

        {/* Gráfico de barras */}
        <motion.div
          className="bg-white rounded-xl shadow-sm border border-slate-100 p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          <h3 className="text-lg font-semibold text-slate-700 mb-4">
            Receitas vs Despesas (6 meses)
          </h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={DADOS_GRAFICO}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="mes" tick={{ fontSize: 13, fill: '#64748b' }} />
              <YAxis tick={{ fontSize: 13, fill: '#64748b' }} tickFormatter={(v) => `R$${(v / 1000).toFixed(0)}k`} />
              <Tooltip
                formatter={(value) => formatCurrency(value)}
                contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }}
              />
              <Legend />
              <Bar dataKey="receitas" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Receitas" />
              <Bar dataKey="despesas" fill="#ef4444" radius={[4, 4, 0, 0]} name="Despesas" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Placeholder para próximos passos */}
        <motion.div
          className="mt-8 bg-brand-50 rounded-xl border border-brand-100 p-6 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <p className="text-brand-700 font-medium">
            🚀 Em breve: categorização por IA, chat inteligente, detecção de anomalias e visual 3D!
          </p>
          <p className="text-brand-500 text-sm mt-2">
            Fase 3 (Scikit-Learn) → Fase 4 (LangChain) → Fase 5 (Three.js + GSAP)
          </p>
        </motion.div>
      </main>
    </div>
  )
}
