import { currentUser } from '@/lib/fixtures/mock-data'
import { User } from '@/lib/types'
import { apiFetch, clearAccessToken, isRestApiConfigured, setAccessToken } from './client'

interface LoginResponse {
  accessToken: string
  tokenType: string
}

export async function login(email: string, password: string) {
  if (!isRestApiConfigured()) {
    setAccessToken('fixture-token')
    return { accessToken: 'fixture-token', tokenType: 'bearer' }
  }

  const response = await apiFetch<LoginResponse>('/auth/login', {
    method: 'POST',
    auth: false,
    body: { email, password },
  })
  setAccessToken(response.accessToken)
  return response
}

export async function register(payload: { email: string; password: string; nickname: string }) {
  if (!isRestApiConfigured()) {
    return {
      ...currentUser,
      email: payload.email,
      nickname: payload.nickname,
    }
  }

  return apiFetch<User>('/auth/register', {
    method: 'POST',
    auth: false,
    body: payload,
  })
}

export async function getAuthenticatedUser() {
  if (!isRestApiConfigured()) return currentUser
  return apiFetch<User>('/auth/me')
}

export function logout() {
  clearAccessToken()
}
