// Types for bola1 World Cup 2026 Prediction App

export interface User {
  id: string
  email: string
  nickname: string
  avatar: string
  isSuperuser?: boolean
  createdAt: string
}

export interface UserPublic {
  id: string
  nickname: string
  avatar: string
  createdAt: string
}

export interface Group {
  id: string
  name: string
  code: string
  inviteLink: string
  createdBy: string
  createdAt: string
  members: GroupMember[]
}

export interface GroupMember {
  userId: string
  user: UserPublic
  role: 'admin' | 'member'
  joinedAt: string
  totalPoints: number
  exactScores: number
  correctWinners: number
  misses: number
}

export interface Team {
  id: string
  name: string
  code: string
  flag: string | null
}

export interface Match {
  id: string
  homeTeam: Team
  awayTeam: Team
  kickoffAt?: string
  date: string
  time: string
  venue: string
  phase: 'group-stage' | 'round-of-16' | 'quarter-finals' | 'semi-finals' | 'final'
  group?: string | null
  status: 'upcoming' | 'live' | 'finished' | 'locked'
  homeScore?: number | null
  awayScore?: number | null
}

export interface Prediction {
  id: string
  matchId: string
  userId: string
  user: UserPublic
  groupId: string
  homeScore: number
  awayScore: number
  points?: number | null
  resultType?: 'exact' | 'winner' | 'miss' | null
  createdAt: string
  updatedAt: string
}

export interface Activity {
  id: string
  type: 'prediction' | 'join' | 'result'
  userId?: string | null
  user: UserPublic | null
  groupId: string
  matchId?: string | null
  match?: Match | null
  prediction?: Prediction | null
  createdAt: string
}

export interface RankingEntry {
  position: number
  user: UserPublic
  totalPoints: number
  exactScores: number
  correctWinners: number
  misses: number
  predictions: number
}
