import { mockPredictions } from '@/lib/fixtures/mock-data'

export const listPredictions = () => mockPredictions

export const listPredictionsForMatch = (matchId: string, groupId: string) =>
  mockPredictions.filter((prediction) => prediction.matchId === matchId && prediction.groupId === groupId)

export const listPredictionsForUser = (userId: string) =>
  mockPredictions.filter((prediction) => prediction.userId === userId)

export const getUserPrediction = (matchId: string, userId: string, groupId: string) =>
  mockPredictions.find((prediction) =>
    prediction.matchId === matchId &&
    prediction.userId === userId &&
    prediction.groupId === groupId
  )
