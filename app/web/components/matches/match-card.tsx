'use client'

import Link from 'next/link'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Match } from '@/lib/types'
import { cn } from '@/lib/utils'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { Lock, Play, CheckCircle2, Clock } from 'lucide-react'

interface MatchCardProps {
  match: Match
  userPrediction?: { homeScore: number; awayScore: number; points?: number }
  compact?: boolean
  showPhase?: boolean
}

export function MatchCard({ match, userPrediction, compact = false, showPhase = false }: MatchCardProps) {
  const statusConfig = {
    upcoming: { label: 'Em breve', color: 'bg-muted text-muted-foreground', icon: Clock },
    live: { label: 'Ao vivo', color: 'bg-destructive text-white animate-pulse', icon: Play },
    finished: { label: 'Encerrado', color: 'bg-success text-success-foreground', icon: CheckCircle2 },
    locked: { label: 'Travado', color: 'bg-warning text-warning-foreground', icon: Lock },
  }

  const status = statusConfig[match.status]
  const StatusIcon = status.icon

  const formattedDate = format(new Date(match.date), "dd 'de' MMM", { locale: ptBR })

  return (
    <Link href={`/matches/${match.id}`}>
      <Card className={cn(
        'overflow-hidden transition-all duration-200 hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]',
        'border-border/50 bg-card',
        compact ? 'p-3' : 'p-4'
      )}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className={cn('text-[10px] font-medium', status.color)}>
              <StatusIcon className="h-3 w-3 mr-1" />
              {status.label}
            </Badge>
            {showPhase && match.group && (
              <Badge variant="outline" className="text-[10px]">
                Grupo {match.group}
              </Badge>
            )}
          </div>
          <span className="text-xs text-muted-foreground">
            {formattedDate} • {match.time}
          </span>
        </div>

        <div className="flex items-center justify-between gap-2">
          {/* Home Team */}
          <div className={cn(
            'flex items-center gap-2',
            compact ? 'flex-1' : 'flex-1 min-w-0'
          )}>
            <span className={cn('shrink-0', compact ? 'text-2xl' : 'text-3xl')}>
              {match.homeTeam.flag}
            </span>
            <div className="min-w-0">
              <p className={cn(
                'font-semibold truncate',
                compact ? 'text-sm' : 'text-base'
              )}>
                {match.homeTeam.name}
              </p>
              <p className="text-[10px] text-muted-foreground uppercase">
                {match.homeTeam.code}
              </p>
            </div>
          </div>

          {/* Score / VS */}
          <div className="flex flex-col items-center px-3">
            {match.status === 'finished' || match.status === 'live' ? (
              <div className="flex items-center gap-2">
                <span className={cn(
                  'font-bold',
                  compact ? 'text-xl' : 'text-2xl'
                )}>
                  {match.homeScore}
                </span>
                <span className="text-muted-foreground">-</span>
                <span className={cn(
                  'font-bold',
                  compact ? 'text-xl' : 'text-2xl'
                )}>
                  {match.awayScore}
                </span>
              </div>
            ) : (
              <span className="text-sm font-medium text-muted-foreground">VS</span>
            )}
            {userPrediction && (
              <div className="mt-1 px-2 py-0.5 rounded-full bg-primary/10">
                <span className="text-[10px] font-medium text-primary">
                  Palpite: {userPrediction.homeScore} - {userPrediction.awayScore}
                </span>
              </div>
            )}
            {userPrediction?.points !== undefined && (
              <Badge className="mt-1 bg-primary text-primary-foreground text-[10px]">
                +{userPrediction.points} pts
              </Badge>
            )}
          </div>

          {/* Away Team */}
          <div className={cn(
            'flex items-center gap-2 justify-end',
            compact ? 'flex-1' : 'flex-1 min-w-0'
          )}>
            <div className="min-w-0 text-right">
              <p className={cn(
                'font-semibold truncate',
                compact ? 'text-sm' : 'text-base'
              )}>
                {match.awayTeam.name}
              </p>
              <p className="text-[10px] text-muted-foreground uppercase">
                {match.awayTeam.code}
              </p>
            </div>
            <span className={cn('shrink-0', compact ? 'text-2xl' : 'text-3xl')}>
              {match.awayTeam.flag}
            </span>
          </div>
        </div>

        {!compact && !userPrediction && match.status === 'upcoming' && (
          <div className="mt-3 pt-3 border-t border-border/50">
            <p className="text-xs text-center text-primary font-medium">
              Manda o palpite
            </p>
          </div>
        )}
      </Card>
    </Link>
  )
}
