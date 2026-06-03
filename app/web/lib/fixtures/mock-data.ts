import { User, Team, Match, Group, Prediction, Activity, RankingEntry } from '@/lib/types'

// Mock Users
export const mockUsers: User[] = [
  { id: 'u1', email: 'joao@email.com', nickname: 'JoãoBoleiro', avatar: '👨‍🦱', createdAt: '2024-01-15' },
  { id: 'u2', email: 'maria@email.com', nickname: 'MariaGol', avatar: '👩‍🦰', createdAt: '2024-02-10' },
  { id: 'u3', email: 'pedro@email.com', nickname: 'PedroCraque', avatar: '🧔', createdAt: '2024-01-20' },
  { id: 'u4', email: 'ana@email.com', nickname: 'AnaTática', avatar: '👩', createdAt: '2024-03-01' },
  { id: 'u5', email: 'carlos@email.com', nickname: 'CarlosPé', avatar: '👨', createdAt: '2024-02-25' },
  { id: 'u6', email: 'lucia@email.com', nickname: 'LuciaBola', avatar: '👧', createdAt: '2024-03-10' },
  { id: 'u7', email: 'rafael@email.com', nickname: 'RafaGoleador', avatar: '🧑', createdAt: '2024-01-05' },
  { id: 'u8', email: 'fernanda@email.com', nickname: 'FêZagueira', avatar: '👩‍🦳', createdAt: '2024-02-15' },
]

export const currentUser = mockUsers[0]

// Mock Teams with flags
export const mockTeams: Team[] = [
  { id: 't1', name: 'Brasil', code: 'BRA', flag: '🇧🇷' },
  { id: 't2', name: 'Argentina', code: 'ARG', flag: '🇦🇷' },
  { id: 't3', name: 'França', code: 'FRA', flag: '🇫🇷' },
  { id: 't4', name: 'Alemanha', code: 'GER', flag: '🇩🇪' },
  { id: 't5', name: 'Espanha', code: 'ESP', flag: '🇪🇸' },
  { id: 't6', name: 'Inglaterra', code: 'ENG', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿' },
  { id: 't7', name: 'Portugal', code: 'POR', flag: '🇵🇹' },
  { id: 't8', name: 'Holanda', code: 'NED', flag: '🇳🇱' },
  { id: 't9', name: 'Itália', code: 'ITA', flag: '🇮🇹' },
  { id: 't10', name: 'Bélgica', code: 'BEL', flag: '🇧🇪' },
  { id: 't11', name: 'Uruguai', code: 'URU', flag: '🇺🇾' },
  { id: 't12', name: 'México', code: 'MEX', flag: '🇲🇽' },
  { id: 't13', name: 'EUA', code: 'USA', flag: '🇺🇸' },
  { id: 't14', name: 'Canadá', code: 'CAN', flag: '🇨🇦' },
  { id: 't15', name: 'Japão', code: 'JPN', flag: '🇯🇵' },
  { id: 't16', name: 'Coreia do Sul', code: 'KOR', flag: '🇰🇷' },
]

// Helper to get team
export const getTeam = (code: string) => mockTeams.find(t => t.code === code)!

// Mock Matches
export const mockMatches: Match[] = [
  // Group Stage - Finished
  {
    id: 'm1',
    homeTeam: getTeam('MEX'),
    awayTeam: getTeam('CAN'),
    date: '2026-06-11',
    time: '17:00',
    venue: 'Estádio Azteca, Cidade do México',
    phase: 'group-stage',
    group: 'A',
    status: 'finished',
    homeScore: 2,
    awayScore: 1,
  },
  {
    id: 'm2',
    homeTeam: getTeam('USA'),
    awayTeam: getTeam('URU'),
    date: '2026-06-11',
    time: '20:00',
    venue: 'MetLife Stadium, Nova York',
    phase: 'group-stage',
    group: 'A',
    status: 'finished',
    homeScore: 1,
    awayScore: 1,
  },
  {
    id: 'm3',
    homeTeam: getTeam('BRA'),
    awayTeam: getTeam('JPN'),
    date: '2026-06-12',
    time: '14:00',
    venue: 'SoFi Stadium, Los Angeles',
    phase: 'group-stage',
    group: 'B',
    status: 'finished',
    homeScore: 3,
    awayScore: 0,
  },
  // Live match
  {
    id: 'm4',
    homeTeam: getTeam('ARG'),
    awayTeam: getTeam('KOR'),
    date: '2026-06-13',
    time: '17:00',
    venue: 'Hard Rock Stadium, Miami',
    phase: 'group-stage',
    group: 'C',
    status: 'live',
    homeScore: 2,
    awayScore: 0,
  },
  // Locked (about to start)
  {
    id: 'm5',
    homeTeam: getTeam('FRA'),
    awayTeam: getTeam('POR'),
    date: '2026-06-13',
    time: '20:00',
    venue: 'AT&T Stadium, Dallas',
    phase: 'group-stage',
    group: 'D',
    status: 'locked',
  },
  // Upcoming matches
  {
    id: 'm6',
    homeTeam: getTeam('GER'),
    awayTeam: getTeam('ESP'),
    date: '2026-06-14',
    time: '14:00',
    venue: 'Mercedes-Benz Stadium, Atlanta',
    phase: 'group-stage',
    group: 'E',
    status: 'upcoming',
  },
  {
    id: 'm7',
    homeTeam: getTeam('ENG'),
    awayTeam: getTeam('NED'),
    date: '2026-06-14',
    time: '17:00',
    venue: 'Levi\'s Stadium, San Francisco',
    phase: 'group-stage',
    group: 'F',
    status: 'upcoming',
  },
  {
    id: 'm8',
    homeTeam: getTeam('ITA'),
    awayTeam: getTeam('BEL'),
    date: '2026-06-14',
    time: '20:00',
    venue: 'Lincoln Financial Field, Filadélfia',
    phase: 'group-stage',
    group: 'G',
    status: 'upcoming',
  },
  {
    id: 'm9',
    homeTeam: getTeam('BRA'),
    awayTeam: getTeam('ARG'),
    date: '2026-06-15',
    time: '17:00',
    venue: 'Rose Bowl, Los Angeles',
    phase: 'group-stage',
    group: 'B',
    status: 'upcoming',
  },
  {
    id: 'm10',
    homeTeam: getTeam('MEX'),
    awayTeam: getTeam('USA'),
    date: '2026-06-15',
    time: '20:00',
    venue: 'Estádio Azteca, Cidade do México',
    phase: 'group-stage',
    group: 'A',
    status: 'upcoming',
  },
  // Round of 16
  {
    id: 'm11',
    homeTeam: getTeam('BRA'),
    awayTeam: getTeam('NED'),
    date: '2026-06-28',
    time: '16:00',
    venue: 'MetLife Stadium, Nova York',
    phase: 'round-of-16',
    status: 'upcoming',
  },
  {
    id: 'm12',
    homeTeam: getTeam('ARG'),
    awayTeam: getTeam('ENG'),
    date: '2026-06-28',
    time: '20:00',
    venue: 'Hard Rock Stadium, Miami',
    phase: 'round-of-16',
    status: 'upcoming',
  },
  // Quarter-finals
  {
    id: 'm13',
    homeTeam: getTeam('FRA'),
    awayTeam: getTeam('GER'),
    date: '2026-07-04',
    time: '17:00',
    venue: 'AT&T Stadium, Dallas',
    phase: 'quarter-finals',
    status: 'upcoming',
  },
  // Semi-finals
  {
    id: 'm14',
    homeTeam: getTeam('BRA'),
    awayTeam: getTeam('FRA'),
    date: '2026-07-08',
    time: '20:00',
    venue: 'SoFi Stadium, Los Angeles',
    phase: 'semi-finals',
    status: 'upcoming',
  },
  // Final
  {
    id: 'm15',
    homeTeam: getTeam('BRA'),
    awayTeam: getTeam('ARG'),
    date: '2026-07-13',
    time: '17:00',
    venue: 'MetLife Stadium, Nova York',
    phase: 'final',
    status: 'upcoming',
  },
]

// Mock Groups
export const mockGroups: Group[] = [
  {
    id: 'g1',
    name: 'Bolão da Firma',
    code: 'FIRMA2026',
    inviteLink: '/groups/join?code=FIRMA2026',
    createdBy: 'u1',
    createdAt: '2024-01-15',
    members: [
      { userId: 'u1', user: mockUsers[0], role: 'admin', joinedAt: '2024-01-15', totalPoints: 24, exactScores: 5, correctWinners: 9, misses: 3 },
      { userId: 'u2', user: mockUsers[1], role: 'member', joinedAt: '2024-01-16', totalPoints: 21, exactScores: 4, correctWinners: 9, misses: 4 },
      { userId: 'u3', user: mockUsers[2], role: 'member', joinedAt: '2024-01-17', totalPoints: 18, exactScores: 3, correctWinners: 9, misses: 5 },
      { userId: 'u4', user: mockUsers[3], role: 'member', joinedAt: '2024-01-18', totalPoints: 15, exactScores: 2, correctWinners: 9, misses: 6 },
      { userId: 'u5', user: mockUsers[4], role: 'member', joinedAt: '2024-01-19', totalPoints: 12, exactScores: 1, correctWinners: 9, misses: 7 },
    ],
  },
  {
    id: 'g2',
    name: 'Família Boleira',
    code: 'FAM2026',
    inviteLink: '/groups/join?code=FAM2026',
    createdBy: 'u1',
    createdAt: '2024-02-01',
    members: [
      { userId: 'u1', user: mockUsers[0], role: 'admin', joinedAt: '2024-02-01', totalPoints: 18, exactScores: 4, correctWinners: 6, misses: 4 },
      { userId: 'u6', user: mockUsers[5], role: 'member', joinedAt: '2024-02-02', totalPoints: 22, exactScores: 5, correctWinners: 7, misses: 2 },
      { userId: 'u7', user: mockUsers[6], role: 'member', joinedAt: '2024-02-03', totalPoints: 15, exactScores: 3, correctWinners: 6, misses: 5 },
    ],
  },
]

// Mock Predictions
export const mockPredictions: Prediction[] = [
  // Match 1 predictions
  { id: 'p1', matchId: 'm1', userId: 'u1', user: mockUsers[0], groupId: 'g1', homeScore: 2, awayScore: 1, points: 3, resultType: 'exact', createdAt: '2026-06-10T10:00:00', updatedAt: '2026-06-10T10:00:00' },
  { id: 'p2', matchId: 'm1', userId: 'u2', user: mockUsers[1], groupId: 'g1', homeScore: 1, awayScore: 0, points: 1, resultType: 'winner', createdAt: '2026-06-10T11:00:00', updatedAt: '2026-06-10T11:00:00' },
  { id: 'p3', matchId: 'm1', userId: 'u3', user: mockUsers[2], groupId: 'g1', homeScore: 0, awayScore: 2, points: 0, resultType: 'miss', createdAt: '2026-06-10T12:00:00', updatedAt: '2026-06-10T12:00:00' },
  // Match 3 predictions
  { id: 'p4', matchId: 'm3', userId: 'u1', user: mockUsers[0], groupId: 'g1', homeScore: 3, awayScore: 0, points: 3, resultType: 'exact', createdAt: '2026-06-11T10:00:00', updatedAt: '2026-06-11T10:00:00' },
  { id: 'p5', matchId: 'm3', userId: 'u2', user: mockUsers[1], groupId: 'g1', homeScore: 2, awayScore: 0, points: 1, resultType: 'winner', createdAt: '2026-06-11T11:00:00', updatedAt: '2026-06-11T11:00:00' },
  // Match 6 predictions (upcoming)
  { id: 'p6', matchId: 'm6', userId: 'u1', user: mockUsers[0], groupId: 'g1', homeScore: 2, awayScore: 2, createdAt: '2026-06-13T10:00:00', updatedAt: '2026-06-13T10:00:00' },
  { id: 'p7', matchId: 'm6', userId: 'u2', user: mockUsers[1], groupId: 'g1', homeScore: 1, awayScore: 2, createdAt: '2026-06-13T11:00:00', updatedAt: '2026-06-13T11:00:00' },
  { id: 'p8', matchId: 'm6', userId: 'u3', user: mockUsers[2], groupId: 'g1', homeScore: 3, awayScore: 1, createdAt: '2026-06-13T12:00:00', updatedAt: '2026-06-13T12:00:00' },
  // Match 9 predictions (Brasil x Argentina - upcoming)
  { id: 'p9', matchId: 'm9', userId: 'u1', user: mockUsers[0], groupId: 'g1', homeScore: 2, awayScore: 1, createdAt: '2026-06-13T14:00:00', updatedAt: '2026-06-13T14:00:00' },
  { id: 'p10', matchId: 'm9', userId: 'u4', user: mockUsers[3], groupId: 'g1', homeScore: 1, awayScore: 3, createdAt: '2026-06-13T15:00:00', updatedAt: '2026-06-13T15:00:00' },
]

// Mock Activities
export const mockActivities: Activity[] = [
  { id: 'a1', type: 'prediction', userId: 'u1', user: mockUsers[0], groupId: 'g1', matchId: 'm9', match: mockMatches.find(m => m.id === 'm9')!, prediction: mockPredictions.find(p => p.id === 'p9')!, createdAt: '2026-06-13T14:00:00' },
  { id: 'a2', type: 'prediction', userId: 'u4', user: mockUsers[3], groupId: 'g1', matchId: 'm9', match: mockMatches.find(m => m.id === 'm9')!, prediction: mockPredictions.find(p => p.id === 'p10')!, createdAt: '2026-06-13T15:00:00' },
  { id: 'a3', type: 'result', userId: 'u1', user: mockUsers[0], groupId: 'g1', matchId: 'm3', match: mockMatches.find(m => m.id === 'm3')!, createdAt: '2026-06-12T16:00:00' },
  { id: 'a4', type: 'prediction', userId: 'u2', user: mockUsers[1], groupId: 'g1', matchId: 'm6', match: mockMatches.find(m => m.id === 'm6')!, prediction: mockPredictions.find(p => p.id === 'p7')!, createdAt: '2026-06-13T11:00:00' },
  { id: 'a5', type: 'join', userId: 'u5', user: mockUsers[4], groupId: 'g1', createdAt: '2026-06-12T09:00:00' },
]

// Generate ranking from group members
export const generateRanking = (groupId: string): RankingEntry[] => {
  const group = mockGroups.find(g => g.id === groupId)
  if (!group) return []

  return group.members
    .map((member, index) => ({
      position: index + 1,
      user: member.user,
      totalPoints: member.totalPoints,
      exactScores: member.exactScores,
      correctWinners: member.correctWinners,
      misses: member.misses,
      predictions: member.exactScores + member.correctWinners + member.misses,
    }))
    .sort((a, b) => b.totalPoints - a.totalPoints)
    .map((entry, index) => ({ ...entry, position: index + 1 }))
}

// Helper functions for API simulation
export const getMatchById = (id: string) => mockMatches.find(m => m.id === id)
export const getGroupById = (id: string) => mockGroups.find(g => g.id === id)
export const getUserById = (id: string) => mockUsers.find(u => u.id === id)
export const getPredictionsForMatch = (matchId: string, groupId: string) =>
  mockPredictions.filter(p => p.matchId === matchId && p.groupId === groupId)
export const getUserPrediction = (matchId: string, userId: string, groupId: string) =>
  mockPredictions.find(p => p.matchId === matchId && p.userId === userId && p.groupId === groupId)
export const getUpcomingMatches = () => mockMatches.filter(m => m.status === 'upcoming')
export const getLiveMatches = () => mockMatches.filter(m => m.status === 'live')
export const getActivitiesForGroup = (groupId: string) =>
  mockActivities.filter(a => a.groupId === groupId).sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())

export const phaseLabels: Record<string, string> = {
  'group-stage': 'Fase de Grupos',
  'round-of-16': 'Oitavas de Final',
  'quarter-finals': 'Quartas de Final',
  'semi-finals': 'Semifinais',
  'final': 'Final',
}

export const statusLabels: Record<string, string> = {
  'upcoming': 'Em breve',
  'live': 'Ao vivo',
  'finished': 'Encerrado',
  'locked': 'Travado',
}
