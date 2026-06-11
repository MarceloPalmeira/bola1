'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { useApp } from '@/lib/context'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { MatchCard } from '@/components/matches/match-card'
import { ActivityFeed } from '@/components/activity/activity-feed'
import { GroupSwitcher } from '@/components/groups/group-switcher'
import { getActivitiesForGroup } from '@/lib/api/activities'
import { listMatches } from '@/lib/api/matches'
import { listPredictionsForUser } from '@/lib/api/predictions'
import { getRanking } from '@/lib/api/rankings'
import { Activity, Match, Prediction, RankingEntry } from '@/lib/types'
import { 
  Trophy, 
  Users, 
  ChevronRight, 
  Zap,
  Share2,
  Sun,
  Moon,
} from 'lucide-react'

export default function DashboardPage() {
  const { currentUser, currentGroup, theme, toggleTheme } = useApp()
  const [matches, setMatches] = useState<Match[]>([])
  const [activities, setActivities] = useState<Activity[]>([])
  const [ranking, setRanking] = useState<RankingEntry[]>([])
  const [userPredictions, setUserPredictions] = useState<Prediction[]>([])

  useEffect(() => {
    let cancelled = false

    async function loadDashboard() {
      const [nextMatches, nextPredictions] = await Promise.all([
        listMatches(),
        currentUser ? listPredictionsForUser(currentUser.id) : Promise.resolve([]),
      ])
      const [nextActivities, nextRanking] = currentGroup
        ? await Promise.all([
            getActivitiesForGroup(currentGroup.id),
            getRanking(currentGroup.id),
          ])
        : [[], []]

      if (cancelled) return
      setMatches(nextMatches)
      setUserPredictions(nextPredictions)
      setActivities(nextActivities.slice(0, 5))
      setRanking(nextRanking)
    }

    loadDashboard()

    return () => {
      cancelled = true
    }
  }, [currentGroup, currentUser])

  const upcomingMatches = matches.filter((match) => match.status === 'upcoming').slice(0, 3)
  const liveMatches = matches.filter((match) => match.status === 'live')
  const currentUserRanking = ranking.find(r => r.user.id === currentUser?.id)
  const currentMember = currentGroup?.members.find(m => m.userId === currentUser?.id)
  const predictionFor = (matchId: string) =>
    userPredictions.find((prediction) => prediction.matchId === matchId && prediction.groupId === currentGroup?.id)

  return (
    <div className="px-4 py-6 max-w-7xl mx-auto">
      {/* Mobile Header */}
      <div className="flex items-center justify-between mb-6 md:hidden">
        <div>
          <h1 className="text-2xl font-bold text-primary">bola1</h1>
          <p className="text-xs text-muted-foreground">Copa do Mundo 2026</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={toggleTheme} className="rounded-full" aria-label="Alternar tema">
            {theme === 'light' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
          </Button>
          <GroupSwitcher />
        </div>
      </div>

      {/* Welcome Card */}
      <Card className="p-4 mb-6 bg-gradient-to-br from-primary/20 via-primary/10 to-transparent border-primary/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-4xl">{currentUser?.avatar}</span>
            <div>
              <p className="text-sm text-muted-foreground">E aí,</p>
              <p className="font-bold text-lg">{currentUser?.nickname}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-primary">{currentMember?.totalPoints || 0}</p>
            <p className="text-xs text-muted-foreground">pontos</p>
          </div>
        </div>
        {currentUserRanking && (
          <div className="mt-4 pt-4 border-t border-border/50 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Trophy className="h-4 w-4 text-primary" />
              <span className="text-sm">
                {currentUserRanking.position}º lugar em {currentGroup?.name}
              </span>
            </div>
            <Link href="/ranking">
              <Button variant="ghost" size="sm" className="text-primary">
                Ver ranking <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </Link>
          </div>
        )}
      </Card>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Main Content Column */}
        <div className="md:col-span-2 space-y-6">
          {/* Live Matches */}
          {liveMatches.length > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-3">
                <Zap className="h-5 w-5 text-destructive" />
                <h2 className="font-semibold">Ao Vivo</h2>
                <Badge variant="destructive" className="animate-pulse text-[10px]">
                  LIVE
                </Badge>
              </div>
              <div className="space-y-3">
                {liveMatches.map((match) => (
                  <MatchCard 
                    key={match.id} 
                    match={match}
                    userPrediction={
                      currentUser && currentGroup
                        ? predictionFor(match.id)
                          ? {
                              homeScore: predictionFor(match.id)!.homeScore,
                              awayScore: predictionFor(match.id)!.awayScore,
                            }
                          : undefined
                        : undefined
                    }
                  />
                ))}
              </div>
            </section>
          )}

          {/* Upcoming Matches */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-semibold">Próximos Jogos</h2>
              <Link href="/matches">
                <Button variant="ghost" size="sm" className="text-muted-foreground">
                  Ver todos <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </Link>
            </div>
            <div className="space-y-3">
              {upcomingMatches.map((match) => {
                const prediction = currentUser && currentGroup
                  ? predictionFor(match.id)
                  : undefined
                return (
                  <MatchCard 
                    key={match.id} 
                    match={match}
                    userPrediction={prediction ? {
                      homeScore: prediction.homeScore,
                      awayScore: prediction.awayScore,
                    } : undefined}
                  />
                )
              })}
            </div>
          </section>

          {/* CTA Card */}
          <Card className="p-4 border-dashed border-2 border-primary/30 bg-primary/5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <Share2 className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="font-medium">Convide seus amigos</p>
                  <p className="text-xs text-muted-foreground">Quanto mais, melhor a zoeira!</p>
                </div>
              </div>
              <Link href={`/groups/${currentGroup?.id}/invite`}>
                <Button size="sm" className="rounded-xl">
                  Convidar
                </Button>
              </Link>
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <Card className="p-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Users className="h-4 w-4" />
              {currentGroup?.name}
            </h3>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="p-2 rounded-lg bg-muted">
                <p className="text-lg font-bold text-success">{currentMember?.exactScores || 0}</p>
                <p className="text-[10px] text-muted-foreground">Placares exatos</p>
              </div>
              <div className="p-2 rounded-lg bg-muted">
                <p className="text-lg font-bold text-primary">{currentMember?.correctWinners || 0}</p>
                <p className="text-[10px] text-muted-foreground">Vencedores</p>
              </div>
              <div className="p-2 rounded-lg bg-muted">
                <p className="text-lg font-bold text-destructive">{currentMember?.misses || 0}</p>
                <p className="text-[10px] text-muted-foreground">Erros</p>
              </div>
            </div>
          </Card>

          {/* Scoring Rules */}
          <Card className="p-4">
            <h3 className="font-semibold mb-3">Como funciona a pontuação</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between p-2 rounded-lg bg-success/10">
                <span>Placar exato</span>
                <Badge className="bg-success text-success-foreground">+3 pts</Badge>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-primary/10">
                <span>Vencedor ou empate certo</span>
                <Badge className="bg-primary text-primary-foreground">+1 pt</Badge>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-destructive/10">
                <span>Errou tudo</span>
                <Badge variant="outline" className="text-destructive">0 pts</Badge>
              </div>
            </div>
          </Card>

          {/* Recent Activity */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold">Atividade recente</h3>
              <Link href="/activity">
                <Button variant="ghost" size="sm" className="text-muted-foreground text-xs">
                  Ver tudo
                </Button>
              </Link>
            </div>
            <ActivityFeed activities={activities.slice(0, 3)} />
          </section>
        </div>
      </div>
    </div>
  )
}
