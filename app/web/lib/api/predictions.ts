import { mockPredictions } from '@/lib/fixtures/mock-data'
import { Prediction } from '@/lib/types'
import { apiFetch, ApiError, isRestApiConfigured } from './client'

export const listPredictions = async () => {
  if (!isRestApiConfigured()) return mockPredictions
  return apiFetch<Prediction[]>('/users/me/predictions')
}

export const listPredictionsForMatch = async (matchId: string, groupId: string) => {
  if (!isRestApiConfigured()) {
    return mockPredictions.filter((prediction) => prediction.matchId === matchId && prediction.groupId === groupId)
  }

  return apiFetch<Prediction[]>(`/groups/${groupId}/matches/${matchId}/predictions`)
}

export const listPredictionsForUser = async (userId?: string) => {
  if (!isRestApiConfigured()) {
    if (!userId) return []
    return mockPredictions.filter((prediction) => prediction.userId === userId)
  }

  return apiFetch<Prediction[]>('/users/me/predictions')
}

export const getUserPrediction = async (matchId: string, userId: string | undefined, groupId: string) => {
  if (!isRestApiConfigured()) {
    return mockPredictions.find((prediction) =>
      prediction.matchId === matchId &&
      prediction.userId === userId &&
      prediction.groupId === groupId
    )
  }

  try {
    return await apiFetch<Prediction>(`/groups/${groupId}/matches/${matchId}/prediction/me`)
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return undefined
    throw error
  }
}

export const savePrediction = async (
  matchId: string,
  groupId: string,
  homeScore: number,
  awayScore: number,
) => {
  if (!isRestApiConfigured()) {
    return mockPredictions.find((prediction) => prediction.matchId === matchId && prediction.groupId === groupId)
  }

  return apiFetch<Prediction>(`/groups/${groupId}/matches/${matchId}/prediction`, {
    method: 'PUT',
    body: { homeScore, awayScore },
  })
}
