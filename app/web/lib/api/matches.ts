import { mockMatches, phaseLabels, statusLabels } from '@/lib/fixtures/mock-data'
import { Match } from '@/lib/types'
import { apiFetch, isRestApiConfigured } from './client'

export { phaseLabels, statusLabels }

export const listMatches = async () => {
  if (!isRestApiConfigured()) return mockMatches
  return apiFetch<Match[]>('/matches')
}

export const getMatch = async (id: string) => {
  if (!isRestApiConfigured()) return mockMatches.find((match) => match.id === id)
  return apiFetch<Match>(`/matches/${id}`)
}

export const listUpcomingMatches = async () => {
  const matches = await listMatches()
  return matches.filter((match) => match.status === 'upcoming')
}

export const listLiveMatches = async () => {
  const matches = await listMatches()
  return matches.filter((match) => match.status === 'live')
}

export const registerMatchResult = async (matchId: string, homeScore: number, awayScore: number) => {
  if (!isRestApiConfigured()) {
    const match = mockMatches.find((item) => item.id === matchId)
    return match
      ? { ...match, status: 'finished' as const, homeScore, awayScore }
      : undefined
  }

  return apiFetch<Match>(`/admin/matches/${matchId}/result`, {
    method: 'POST',
    body: { homeScore, awayScore },
  })
}
