/**
 * auth.js — Funções de autenticação (chamadas à API).
 *
 * Cada função encapsula uma chamada HTTP. Os componentes
 * chamam estas funções em vez de mexer com axios diretamente.
 *
 * Princípio SOLID 'S': esta camada só sabe sobre endpoints de auth.
 */
import api from './client'

/**
 * Cadastra um novo usuário.
 * @param {{ name: string, email: string, password: string }} data
 * @returns {Promise<{ id: number, name: string, email: string }>}
 */
export async function register({ name, email, password }) {
  const response = await api.post('/auth/register', { name, email, password })
  return response.data
}

/**
 * Faz login e recebe o token JWT.
 * @param {{ email: string, password: string }} data
 * @returns {Promise<{ access_token: string, token_type: string, user: object }>}
 */
export async function login({ email, password }) {
  const response = await api.post('/auth/login', { email, password })
  return response.data
}
