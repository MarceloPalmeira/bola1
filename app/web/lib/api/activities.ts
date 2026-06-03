import { getActivitiesForGroup as getFixtureActivitiesForGroup } from '@/lib/fixtures/mock-data'

export const getActivitiesForGroup = (groupId: string) =>
  getFixtureActivitiesForGroup(groupId)
