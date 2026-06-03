// Types for bola1 World Cup 2026 Prediction App

export interface User {
  id: string
  email: string
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
  user: User
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
  flag: string
}

export interface Match {
  id: string
  homeTeam: Team
  awayTeam: Team
  date: string
  time: string
  venue: string
  phase: 'group-stage' | 'round-of-16' | 'quarter-finals' | 'semi-finals' | 'final'
  group?: string
  status: 'upcoming' | 'live' | 'finished' | 'locked'
  homeScore?: number
  awayScore?: number
}

export interface Prediction {
  id: string
  matchId: string
  userId: string
  user: User
  groupId: string
  homeScore: number
  awayScore: number
  points?: number
  resultType?: 'exact' | 'winner' | 'miss'
  createdAt: string
  updatedAt: string
}

export interface Activity {
  id: string
  type: 'prediction' | 'join' | 'result'
  userId: string
  user: User
  groupId: string
  matchId?: string
  match?: Match
  prediction?: Prediction
  createdAt: string
}

export interface RankingEntry {
  position: number
  user: User
  totalPoints: number
  exactScores: number
  correctWinners: number
  misses: number
  predictions: number
}
