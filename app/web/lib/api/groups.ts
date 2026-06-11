import { mockGroups } from '@/lib/fixtures/mock-data'
import { Group } from '@/lib/types'
import { apiFetch, isRestApiConfigured } from './client'

export const listGroups = async () => {
  if (!isRestApiConfigured()) return mockGroups
  return apiFetch<Group[]>('/groups')
}

export const getCurrentGroup = async () => {
  const groups = await listGroups()
  return groups[0] ?? null
}

export const listUserGroups = async (userId?: string) => {
  if (!isRestApiConfigured()) {
    if (!userId) return []
    return mockGroups.filter((group) =>
      group.members.some((member) => member.userId === userId)
    )
  }

  return listGroups()
}

export const getGroup = async (id: string) => {
  if (!isRestApiConfigured()) return mockGroups.find((group) => group.id === id)
  return apiFetch<Group>(`/groups/${id}`)
}

export const createGroup = async (name: string) => {
  if (!isRestApiConfigured()) {
    return mockGroups[0]
  }

  return apiFetch<Group>('/groups', {
    method: 'POST',
    body: { name },
  })
}

export const joinGroup = async (code: string) => {
  if (!isRestApiConfigured()) {
    return mockGroups.find((group) => group.code === code.toUpperCase()) ?? mockGroups[0]
  }

  return apiFetch<Group>('/groups/join', {
    method: 'POST',
    body: { code },
  })
}
