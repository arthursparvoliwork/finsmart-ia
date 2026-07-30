/**
 * transactions.js — Funções de transações (chamadas à API).
 *
 * Cada função encapsula uma chamada HTTP. O token JWT é adicionado
 * automaticamente pelo interceptor do client.js (não precisamos fazer nada).
 */
import api from './client'

/**
 * Lista todas as transações do usuário logado.
 * @returns {Promise<Array>}
 */
export async function listTransactions() {
  const res = await api.get('/transactions')
  return res.data
}

/**
 * Cria uma nova transação.
 * @param {object} data - { valor, data, descricao, tipo, categoria?, observacoes? }
 */
export async function createTransaction(data) {
  const res = await api.post('/transactions', data)
  return res.data
}

/**
 * Atualiza uma transação existente.
 * @param {number} id
 * @param {object} data - campos a atualizar
 */
export async function updateTransaction(id, data) {
  const res = await api.put(`/transactions/${id}`, data)
  return res.data
}

/**
 * Remove uma transação.
 * @param {number} id
 */
export async function deleteTransaction(id) {
  const res = await api.delete(`/transactions/${id}`)
  return res.data
}

/**
 * Pede pra IA categorizar uma descrição (sem salvar no banco).
 * Útil pra mostrar a categoria em tempo real enquanto o usuário digita.
 * @param {string} descricao
 * @returns {Promise<{ descricao, categoria, confianca }>}
 */
export async function categorizeWithAI(descricao) {
  const res = await api.post('/transactions/categorizar', { descricao })
  return res.data
}

/**
 * Busca o resumo financeiro (totais para dashboard).
 * @returns {Promise<{ total_receitas, total_despesas, saldo }>}
 */
export async function getSummary() {
  const res = await api.get('/transactions/resumo')
  return res.data
}
