import { getActivitiesForGroup as getFixtureActivitiesForGroup } from '@/lib/fixtures/mock-data'
import { Activity } from '@/lib/types'
import { apiFetch, isRestApiConfigured } from './client'

export const getActivitiesForGroup = async (groupId: string) => {
  if (!isRestApiConfigured()) return getFixtureActivitiesForGroup(groupId)
  return apiFetch<Activity[]>(`/groups/${groupId}/activities`)
}
