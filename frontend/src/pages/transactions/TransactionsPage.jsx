/**
 * TransactionsPage.jsx — Página de transações do usuário.
 *
 * 🎓 RECURSOS DESTA PÁGINA:
 * - Formulário para adicionar transação
 * - CATEGORIZAÇÃO IA EM TEMPO REAL: enquanto digita a descrição,
 *   chama a IA e mostra a categoria prevista (com badge de confiança)
 * - Lista de transações existentes
 * - Excluir transações
 * - Animações Framer Motion (lista animada, entrada de novos itens)
 *
 * 🎓 DEBOUNCE:
 * Pra não chamar a IA a cada tecla (seria pesado), usamos um "debounce":
 * só chama a IA 600ms depois que o usuário PAROU de digitar.
 */
import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  listTransactions,
  createTransaction,
  deleteTransaction,
  categorizeWithAI,
} from '@/api/transactions'

// Mapa de cores por categoria (pra deixar a UI bonita)
const CORES_CATEGORIA = {
  'Alimentação': 'bg-orange-100 text-orange-700',
  'Transporte': 'bg-blue-100 text-blue-700',
  'Moradia': 'bg-purple-100 text-purple-700',
  'Saude': 'bg-red-100 text-red-700',
  'Lazer': 'bg-pink-100 text-pink-700',
  'Compras': 'bg-yellow-100 text-yellow-700',
  'Renda': 'bg-green-100 text-green-700',
  'Educação': 'bg-indigo-100 text-indigo-700',
  'Assinaturas': 'bg-cyan-100 text-cyan-700',
  'Transferencias': 'bg-gray-100 text-gray-700',
}

function BadgeCategoria({ categoria }) {
  if (!categoria) return null
  const cor = CORES_CATEGORIA[categoria] || 'bg-slate-100 text-slate-700'
  return (
    <span className={`text-xs font-semibold px-2 py-1 rounded-full ${cor}`}>
      {categoria}
    </span>
  )
}

export default function TransactionsPage() {
  const [transacoes, setTransacoes] = useState([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')

  // Formulário
  const [form, setForm] = useState({
    descricao: '',
    valor: '',
    data: new Date().toISOString().split('T')[0],
    tipo: 'despesa',
  })
  const [salvando, setSalvando] = useState(false)

  // IA: categoria prevista enquanto digita
  const [categoriaIA, setCategoriaIA] = useState(null)
  const [confiancaIA, setConfiancaIA] = useState(0)

  // Carrega transações
  const carregar = useCallback(async () => {
    try {
      setLoading(true)
      const dados = await listTransactions()
      setTransacoes(dados)
    } catch {
      setErro('Erro ao carregar transações')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    carregar()
  }, [carregar])

  // =====================================================
  // CATEGORIZAÇÃO IA EM TEMPO REAL (com debounce)
  // =====================================================
  // Sempre que a descrição muda, espera 600ms e chama a IA.
  useEffect(() => {
    if (!form.descricao || form.descricao.length < 3) {
      setCategoriaIA(null)
      return
    }
    const timer = setTimeout(async () => {
      try {
        const resultado = await categorizeWithAI(form.descricao)
        setCategoriaIA(resultado.categoria)
        setConfiancaIA(resultado.confianca)
      } catch {
        // falhou silenciosamente (IA é opcional, não trava o form)
      }
    }, 600) // debounce 600ms
    return () => clearTimeout(timer)
  }, [form.descricao])

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSalvando(true)
    setErro('')
    try {
      // Envia. A IA no backend categoriza automaticamente.
      await createTransaction({
        descricao: form.descricao,
        valor: parseFloat(form.valor),
        data: form.data,
        tipo: form.tipo,
      })
      // Limpa o form
      setForm({
        descricao: '',
        valor: '',
        data: new Date().toISOString().split('T')[0],
        tipo: 'despesa',
      })
      setCategoriaIA(null)
      // Recarrega a lista
      await carregar()
    } catch (err) {
      setErro(err.response?.data?.error || 'Erro ao salvar')
    } finally {
      setSalvando(false)
    }
  }

  async function handleDelete(id) {
    try {
      await deleteTransaction(id)
      setTransacoes(transacoes.filter((t) => t.id !== id))
    } catch {
      setErro('Erro ao excluir')
    }
  }

  function formatCurrency(v) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency', currency: 'BRL'
    }).format(parseFloat(v))
  }

  function formatDate(isoString) {
    const d = new Date(isoString)
    return d.toLocaleDateString('pt-BR')
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-100 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-6">
          <a href="/dashboard" className="flex items-center gap-2">
            <span className="text-2xl">🏦</span>
            <h1 className="text-xl font-bold text-brand-700">FinSmart IA</h1>
          </a>
          <a href="/dashboard" className="text-sm text-slate-500 hover:text-brand-600">
            ← Voltar ao dashboard
          </a>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* ===================== FORMULÁRIO (esquerda) ===================== */}
        <motion.div
          className="lg:col-span-2"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6 sticky top-24">
            <h2 className="text-lg font-semibold text-slate-800 mb-4">
              ➕ Nova transação
            </h2>

            {erro && (
              <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4">
                {erro}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Descrição + preview da categoria IA */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Descrição
                </label>
                <input
                  type="text"
                  name="descricao"
                  value={form.descricao}
                  onChange={handleChange}
                  required
                  placeholder="Ex: iFood, Uber, Salário..."
                  className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none transition-all"
                />
                {/* Preview da IA em tempo real */}
                <AnimatePresence>
                  {categoriaIA && (
                    <motion.div
                      className="flex items-center gap-2 mt-2 text-xs"
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                    >
                      <span className="text-slate-400">🤖 IA previu:</span>
                      <BadgeCategoria categoria={categoriaIA} />
                      <span className="text-slate-400">
                        ({Math.round(confiancaIA * 100)}% confiança)
                      </span>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Valor + Tipo */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Valor (R$)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="valor"
                    value={form.valor}
                    onChange={handleChange}
                    required
                    placeholder="0,00"
                    className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Tipo
                  </label>
                  <select
                    name="tipo"
                    value={form.tipo}
                    onChange={handleChange}
                    className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none transition-all bg-white"
                  >
                    <option value="despesa">Despesa</option>
                    <option value="receita">Receita</option>
                  </select>
                </div>
              </div>

              {/* Data */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Data
                </label>
                <input
                  type="date"
                  name="data"
                  value={form.data}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none transition-all"
                />
              </div>

              <motion.button
                type="submit"
                disabled={salvando}
                className="w-full py-3 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {salvando ? '⏳ Salvando...' : 'Salvar transação'}
              </motion.button>
            </form>
          </div>
        </motion.div>

        {/* ===================== LISTA (direita) ===================== */}
        <motion.div
          className="lg:col-span-3"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-4">
              📋 Minhas transações
            </h2>

            {loading ? (
              <p className="text-slate-400 text-center py-8">Carregando...</p>
            ) : transacoes.length === 0 ? (
              <p className="text-slate-400 text-center py-8">
                Nenhuma transação ainda. Adicione a primeira! 👆
              </p>
            ) : (
              <ul className="divide-y divide-slate-100">
                <AnimatePresence>
                  {transacoes.map((t) => (
                    <motion.li
                      key={t.id}
                      layout
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, x: -50 }}
                      className="py-3 flex items-center justify-between gap-3"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-medium text-slate-800 truncate">
                            {t.descricao}
                          </span>
                          <BadgeCategoria categoria={t.categoria} />
                        </div>
                        <div className="text-xs text-slate-400 mt-0.5">
                          {formatDate(t.data)}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`font-semibold ${
                          t.tipo === 'receita' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {t.tipo === 'receita' ? '+' : '-'}{formatCurrency(t.valor)}
                        </span>
                        <motion.button
                          onClick={() => handleDelete(t.id)}
                          className="text-slate-300 hover:text-red-500 transition-colors"
                          whileHover={{ scale: 1.2 }}
                          whileTap={{ scale: 0.9 }}
                        >
                          🗑️
                        </motion.button>
                      </div>
                    </motion.li>
                  ))}
                </AnimatePresence>
              </ul>
            )}
          </div>
        </motion.div>
      </main>
    </div>
  )
}
