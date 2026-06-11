import { generateRanking } from '@/lib/fixtures/mock-data'
import { RankingEntry } from '@/lib/types'
import { apiFetch, isRestApiConfigured } from './client'

export const getRanking = async (groupId: string) => {
  if (!isRestApiConfigured()) return generateRanking(groupId)
  return apiFetch<RankingEntry[]>(`/groups/${groupId}/ranking`)
}
