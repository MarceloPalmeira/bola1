'use client'

import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { MatchCard } from '@/components/matches/match-card'
import { listMatches } from '@/lib/api/matches'
import { listPredictionsForUser } from '@/lib/api/predictions'
import { useApp } from '@/lib/context'
import { Match, Prediction } from '@/lib/types'
import { Calendar } from 'lucide-react'

const phases = [
  { value: 'all', label: 'Todos' },
  { value: 'group-stage', label: 'Grupos' },
  { value: 'round-of-16', label: 'Oitavas' },
  { value: 'quarter-finals', label: 'Quartas' },
  { value: 'semi-finals', label: 'Semis' },
  { value: 'final', label: 'Final' },
]

const statuses = [
  { value: 'all', label: 'Todos', color: 'bg-muted' },
  { value: 'upcoming', label: 'Em breve', color: 'bg-muted' },
  { value: 'live', label: 'Ao vivo', color: 'bg-destructive' },
  { value: 'finished', label: 'Encerrados', color: 'bg-success' },
]

export default function MatchesPage() {
  const { currentUser, currentGroup } = useApp()
  const [selectedPhase, setSelectedPhase] = useState('all')
  const [selectedStatus, setSelectedStatus] = useState('all')
  const [matches, setMatches] = useState<Match[]>([])
  const [userPredictions, setUserPredictions] = useState<Prediction[]>([])

  useEffect(() => {
    let cancelled = false

    async function loadMatches() {
      const [nextMatches, nextPredictions] = await Promise.all([
        listMatches(),
        currentUser ? listPredictionsForUser(currentUser.id) : Promise.resolve([]),
      ])
      if (cancelled) return
      setMatches(nextMatches)
      setUserPredictions(nextPredictions)
    }

    loadMatches()

    return () => {
      cancelled = true
    }
  }, [currentUser])

  const filteredMatches = matches.filter((match) => {
    const phaseMatch = selectedPhase === 'all' || match.phase === selectedPhase
    const statusMatch = selectedStatus === 'all' || match.status === selectedStatus
    return phaseMatch && statusMatch
  })

  const upcomingCount = matches.filter(m => m.status === 'upcoming').length
  const liveCount = matches.filter(m => m.status === 'live').length

  return (
    <div className="px-4 py-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <Calendar className="h-5 w-5 text-primary" />
          <h1 className="text-xl font-bold">Jogos</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          Copa do Mundo 2026 - {matches.length} partidas
        </p>
      </div>

      {/* Quick Stats */}
      <div className="flex gap-3 mb-6 overflow-x-auto scrollbar-hide pb-2">
        <Card className="flex-shrink-0 px-4 py-3 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
            <span className="text-lg font-bold">{upcomingCount}</span>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Jogos</p>
            <p className="font-medium text-sm">a palpitar</p>
          </div>
        </Card>
        {liveCount > 0 && (
          <Card className="flex-shrink-0 px-4 py-3 flex items-center gap-3 border-destructive/50 bg-destructive/5">
            <div className="w-10 h-10 rounded-full bg-destructive/20 flex items-center justify-center">
              <span className="text-lg font-bold text-destructive">{liveCount}</span>
            </div>
            <div>
              <p className="text-xs text-destructive">Jogos</p>
              <p className="font-medium text-sm text-destructive">ao vivo agora</p>
            </div>
          </Card>
        )}
      </div>

      {/* Phase Tabs */}
      <Tabs value={selectedPhase} onValueChange={setSelectedPhase} className="mb-4">
        <TabsList className="w-full justify-start overflow-x-auto scrollbar-hide h-auto p-1 bg-muted rounded-xl">
          {phases.map((phase) => (
            <TabsTrigger
              key={phase.value}
              value={phase.value}
              className="rounded-lg text-xs px-3 py-2 data-[state=active]:bg-card data-[state=active]:shadow-sm"
            >
              {phase.label}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Status Filter */}
      <div className="flex gap-2 mb-6 overflow-x-auto scrollbar-hide pb-2">
        {statuses.map((status) => (
          <Button
            key={status.value}
            variant={selectedStatus === status.value ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedStatus(status.value)}
            className="rounded-full text-xs shrink-0"
          >
            {status.value !== 'all' && (
              <span className={`w-2 h-2 rounded-full ${status.color} mr-2`} />
            )}
            {status.label}
          </Button>
        ))}
      </div>

      {/* Matches List */}
      {filteredMatches.length === 0 ? (
        <Card className="p-8 text-center">
          <div className="text-4xl mb-3">🔍</div>
          <p className="font-medium">Nenhum jogo encontrado</p>
          <p className="text-sm text-muted-foreground">
            Tente ajustar os filtros
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {filteredMatches.map((match) => {
            const prediction = currentUser && currentGroup
              ? userPredictions.find((item) => item.matchId === match.id && item.groupId === currentGroup.id)
              : undefined
            return (
              <MatchCard
                key={match.id}
                match={match}
                showPhase={selectedPhase === 'all'}
                userPrediction={prediction ? {
                  homeScore: prediction.homeScore,
                  awayScore: prediction.awayScore,
                  points: prediction.points,
                } : undefined}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}
