import { mockMatches, phaseLabels, statusLabels } from '@/lib/fixtures/mock-data'
import { Match } from '@/lib/types'
import { apiFetch, isRestApiConfigured } from './client'

export { phaseLabels, statusLabels }

const warnMockFallback = (fn: string) => {
  if (process.env.NODE_ENV !== 'development') {
    console.error(
      `[bola1] ${fn}: NEXT_PUBLIC_API_URL is not set — returning fixture data. ` +
      'Configure the variable before deploying to production.',
    )
  }
}

export const listMatches = async () => {
  if (!isRestApiConfigured()) {
    warnMockFallback('listMatches')
    return mockMatches
  }
  return apiFetch<Match[]>('/matches')
}

export const getMatch = async (id: string) => {
  if (!isRestApiConfigured()) {
    warnMockFallback('getMatch')
    return mockMatches.find((match) => match.id === id)
  }
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
    warnMockFallback('registerMatchResult')
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

export const syncMatchesFromApi = async (competitionId = '2000') => {
  if (!isRestApiConfigured()) {
    warnMockFallback('syncMatchesFromApi')
    return { status: 'ok', synced: 0, skipped: 0 }
  }
  return apiFetch<{ status: string; synced: number; skipped: number }>(
    `/admin/matches/sync?competition_id=${competitionId}`,
    { method: 'POST' },
  )
}

export const recalculateAllRankings = async () => {
  if (!isRestApiConfigured()) {
    warnMockFallback('recalculateAllRankings')
    return { status: 'ok' }
  }
  return apiFetch<{ status: string }>('/admin/rankings/recalculate', { method: 'POST' })
}
