import { mockMatches, phaseLabels, statusLabels } from '@/lib/fixtures/mock-data'

export { phaseLabels, statusLabels }

export const listMatches = () => mockMatches

export const getMatch = (id: string) => mockMatches.find((match) => match.id === id)

export const listUpcomingMatches = () =>
  mockMatches.filter((match) => match.status === 'upcoming')

export const listLiveMatches = () =>
  mockMatches.filter((match) => match.status === 'live')
