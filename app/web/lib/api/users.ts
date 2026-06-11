import { currentUser, mockUsers } from '@/lib/fixtures/mock-data'
import { User } from '@/lib/types'
import { apiFetch, isRestApiConfigured } from './client'

export const getCurrentUser = async () => {
  if (!isRestApiConfigured()) return currentUser
  return apiFetch<User>('/auth/me')
}

export const listUsers = async () => mockUsers

export const getUser = async (id: string) => {
  if (!isRestApiConfigured()) return mockUsers.find((user) => user.id === id)
  const me = await getCurrentUser()
  return me.id === id ? me : undefined
}
