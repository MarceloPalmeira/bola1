'use client'

import { use, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { ScoreSelector } from '@/components/matches/score-selector'
import { useApp } from '@/lib/context'
import { getMatch, phaseLabels, statusLabels } from '@/lib/api/matches'
import { listPredictionsForMatch, getUserPrediction, savePrediction } from '@/lib/api/predictions'
import { Match, Prediction } from '@/lib/types'
import { 
  ArrowLeft, 
  Calendar, 
  MapPin, 
  Clock, 
  Lock,
  Target,
  ThumbsUp,
  X,
  Users,
} from 'lucide-react'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

interface MatchDetailPageProps {
  params: Promise<{ id: string }>
}

export default function MatchDetailPage({ params }: MatchDetailPageProps) {
  const { id } = use(params)
  const router = useRouter()
  const { currentUser, currentGroup } = useApp()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [match, setMatch] = useState<Match | undefined>()
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [userPrediction, setUserPrediction] = useState<Prediction | undefined>()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function loadMatch() {
      setIsLoading(true)
      try {
        const [nextMatch, nextPredictions, nextUserPrediction] = await Promise.all([
          getMatch(id),
          currentGroup ? listPredictionsForMatch(id, currentGroup.id) : Promise.resolve([]),
          currentUser && currentGroup
            ? getUserPrediction(id, currentUser.id, currentGroup.id)
            : Promise.resolve(undefined),
        ])
        if (cancelled) return
        setMatch(nextMatch)
        setPredictions(nextPredictions)
        setUserPrediction(nextUserPrediction)
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    loadMatch()

    return () => {
      cancelled = true
    }
  }, [currentGroup, currentUser, id])

  if (!match && !isLoading) {
    return (
      <div className="px-4 py-6 max-w-2xl mx-auto">
        <Card className="p-8 text-center">
          <div className="text-4xl mb-3">🤔</div>
          <p className="font-medium">Jogo não encontrado</p>
          <Button variant="outline" className="mt-4" onClick={() => router.back()}>
            Voltar
          </Button>
        </Card>
      </div>
    )
  }

  if (!match) {
    return (
      <div className="px-4 py-6 max-w-2xl mx-auto">
        <Card className="p-8 text-center">
          <p className="font-medium">Carregando jogo...</p>
        </Card>
      </div>
    )
  }

  const isLocked = match.status === 'locked' || match.status === 'live' || match.status === 'finished'
  const formattedDate = format(new Date(match.date), "EEEE, dd 'de' MMMM", { locale: ptBR })

  const handleSubmitPrediction = async (homeScore: number, awayScore: number) => {
    if (!currentGroup) return
    setIsSubmitting(true)
    try {
      const savedPrediction = await savePrediction(match.id, currentGroup.id, homeScore, awayScore)
      if (savedPrediction) {
        setUserPrediction(savedPrediction)
        setPredictions((items) => [
          savedPrediction,
          ...items.filter((prediction) => prediction.id !== savedPrediction.id),
        ])
      }
      toast.success('Palpite registrado!', {
        description: `${match.homeTeam.name} ${homeScore} x ${awayScore} ${match.awayTeam.name}`,
      })
    } catch {
      toast.error('Não foi possível registrar o palpite')
    } finally {
      setIsSubmitting(false)
    }
  }

  const getResultBadge = (resultType?: 'exact' | 'winner' | 'miss' | null) => {
    if (!resultType) return null
    const config = {
      exact: { label: 'Acertou na mosca!', icon: Target, color: 'bg-success text-success-foreground' },
      winner: { label: 'Foi de base', icon: ThumbsUp, color: 'bg-primary text-primary-foreground' },
      miss: { label: 'Não foi dessa vez', icon: X, color: 'bg-destructive/10 text-destructive' },
    }
    const c = config[resultType]
    return (
      <Badge className={cn('text-xs', c.color)}>
        <c.icon className="h-3 w-3 mr-1" />
        {c.label}
      </Badge>
    )
  }

  return (
    <div className="px-4 py-6 max-w-2xl mx-auto">
      {/* Back Button */}
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={() => router.back()}
        className="mb-4 -ml-2"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Voltar
      </Button>

      {/* Match Header Card */}
      <Card className="p-4 sm:p-6 mb-6 overflow-hidden">
        {/* Status & Phase */}
        <div className="flex items-center justify-between mb-6">
          <Badge 
            variant="secondary"
            className={cn(
              'text-xs',
              match.status === 'live' && 'bg-destructive text-white animate-pulse',
              match.status === 'finished' && 'bg-success text-success-foreground',
              match.status === 'locked' && 'bg-warning text-warning-foreground',
            )}
          >
            {match.status === 'live' && <span className="w-2 h-2 rounded-full bg-white mr-2" />}
            {statusLabels[match.status]}
          </Badge>
          <Badge variant="outline" className="text-xs">
            {phaseLabels[match.phase]}
            {match.group && ` - Grupo ${match.group}`}
          </Badge>
        </div>

        {/* Teams */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex-1 text-center">
            <span className="text-6xl block mb-2">{match.homeTeam.flag}</span>
            <p className="font-bold text-lg">{match.homeTeam.name}</p>
            <p className="text-xs text-muted-foreground uppercase">{match.homeTeam.code}</p>
          </div>
          
          <div className="px-4 text-center">
            {(match.status === 'finished' || match.status === 'live') ? (
              <div className="flex items-center gap-3">
                <span className="text-4xl font-bold">{match.homeScore}</span>
                <span className="text-2xl text-muted-foreground">-</span>
                <span className="text-4xl font-bold">{match.awayScore}</span>
              </div>
            ) : (
              <span className="text-2xl font-bold text-muted-foreground">VS</span>
            )}
          </div>

          <div className="flex-1 text-center">
            <span className="text-6xl block mb-2">{match.awayTeam.flag}</span>
            <p className="font-bold text-lg">{match.awayTeam.name}</p>
            <p className="text-xs text-muted-foreground uppercase">{match.awayTeam.code}</p>
          </div>
        </div>

        {/* Match Info */}
        <div className="flex flex-wrap items-center justify-center gap-4 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Calendar className="h-4 w-4" />
            {formattedDate}
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            {match.time}
          </span>
        </div>
        <p className="text-center text-xs text-muted-foreground mt-2 flex items-center justify-center gap-1">
          <MapPin className="h-3 w-3" />
          {match.venue}
        </p>
      </Card>

      {/* User Prediction Result (if match finished) */}
      {match.status === 'finished' && userPrediction && (
        <Card className="p-4 mb-6 bg-gradient-to-r from-primary/10 to-transparent">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Seu palpite</p>
              <p className="text-2xl font-bold">
                {userPrediction.homeScore} - {userPrediction.awayScore}
              </p>
            </div>
            <div className="text-right">
              {getResultBadge(userPrediction.resultType)}
              {userPrediction.points != null && (
                <p className="text-2xl font-bold text-primary mt-1">
                  +{userPrediction.points} pts
                </p>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Score Selector (if not locked) */}
      {!isLocked && (
        <Card className="p-4 sm:p-6 mb-6">
          <h2 className="font-semibold mb-4 text-center">
            {userPrediction ? 'Atualizar palpite' : 'Manda o palpite!'}
          </h2>
          <ScoreSelector
            homeTeam={match.homeTeam}
            awayTeam={match.awayTeam}
            initialHomeScore={userPrediction?.homeScore}
            initialAwayScore={userPrediction?.awayScore}
            onSubmit={handleSubmitPrediction}
            isLocked={isLocked}
            isUpdating={isSubmitting}
          />
        </Card>
      )}

      {/* Locked State */}
      {isLocked && !userPrediction && match.status !== 'finished' && (
        <Card className="p-6 mb-6 text-center bg-muted/50">
          <Lock className="h-8 w-8 mx-auto mb-3 text-muted-foreground" />
          <p className="font-medium">Palpite travado</p>
          <p className="text-sm text-muted-foreground">
            Você não registrou um palpite para este jogo
          </p>
        </Card>
      )}

      {/* Friends Predictions */}
      <Card className="p-4">
        <div className="flex items-center gap-2 mb-4">
          <Users className="h-4 w-4 text-primary" />
          <h2 className="font-semibold">Palpites do grupo</h2>
          <Badge variant="secondary" className="text-xs">
            {predictions.length} palpites
          </Badge>
        </div>

        {predictions.length === 0 ? (
          <div className="text-center py-6">
            <div className="text-3xl mb-2">👀</div>
            <p className="text-sm text-muted-foreground">
              Seu grupo ainda está secando. Seja o primeiro!
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {predictions.map((prediction) => (
              <div 
                key={prediction.id}
                className={cn(
                  'flex items-center gap-3 p-3 rounded-xl',
                  prediction.userId === currentUser?.id ? 'bg-primary/10' : 'bg-muted/50'
                )}
              >
                <Avatar className="h-10 w-10">
                  <AvatarFallback className="text-lg bg-background">
                    {prediction.user.avatar}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">
                    {prediction.user.nickname}
                    {prediction.userId === currentUser?.id && (
                      <Badge variant="outline" className="ml-2 text-[10px]">Você</Badge>
                    )}
                  </p>
                  {match.status === 'finished' && getResultBadge(prediction.resultType)}
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold">
                    {prediction.homeScore} - {prediction.awayScore}
                  </p>
                  {prediction.points != null && (
                    <p className="text-xs text-primary font-medium">
                      +{prediction.points} pts
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
