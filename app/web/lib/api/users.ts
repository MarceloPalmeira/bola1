import { currentUser, mockUsers } from '@/lib/fixtures/mock-data'

export const getCurrentUser = () => currentUser

export const listUsers = () => mockUsers

export const getUser = (id: string) => mockUsers.find((user) => user.id === id)
