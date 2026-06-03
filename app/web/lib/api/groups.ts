import { mockGroups } from '@/lib/fixtures/mock-data'

export const listGroups = () => mockGroups

export const getCurrentGroup = () => mockGroups[0] ?? null

export const listUserGroups = (userId?: string) => {
  if (!userId) return []

  return mockGroups.filter((group) =>
    group.members.some((member) => member.userId === userId)
  )
}

export const getGroup = (id: string) => mockGroups.find((group) => group.id === id)
