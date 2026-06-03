'use client'

import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Activity } from '@/lib/types'
import { cn } from '@/lib/utils'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { Target, ThumbsUp, X, Users } from 'lucide-react'

interface ActivityFeedProps {
  activities: Activity[]
}

export function ActivityFeed({ activities }: ActivityFeedProps) {
  if (activities.length === 0) {
    return (
      <Card className="p-8 text-center">
        <div className="text-4xl mb-3">📭</div>
        <p className="font-medium">Nenhuma atividade ainda</p>
        <p className="text-sm text-muted-foreground">
          Seu grupo ainda está em silêncio. Chama a galera!
        </p>
      </Card>
    )
  }

  return (
    <div className="space-y-3">
      {activities.map((activity) => (
        <ActivityItem key={activity.id} activity={activity} />
      ))}
    </div>
  )
}

function ActivityItem({ activity }: { activity: Activity }) {
  const timeAgo = formatDistanceToNow(new Date(activity.createdAt), {
    addSuffix: true,
    locale: ptBR,
  })

  if (activity.type === 'join') {
    return (
      <Card className="p-3 flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-success/10 flex items-center justify-center">
          <Users className="h-5 w-5 text-success" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm">
            <span className="font-medium">{activity.user.nickname}</span>
            {' entrou no grupo'}
          </p>
          <p className="text-xs text-muted-foreground">{timeAgo}</p>
        </div>
        <span className="text-2xl">{activity.user.avatar}</span>
      </Card>
    )
  }

  if (activity.type === 'result' && activity.match) {
    return (
      <Card className="p-3 flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
          <Target className="h-5 w-5 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium">
            Resultado registrado
          </p>
          <p className="text-xs text-muted-foreground">
            {activity.match.homeTeam.flag} {activity.match.homeTeam.name} {activity.match.homeScore} x {activity.match.awayScore} {activity.match.awayTeam.name} {activity.match.awayTeam.flag}
          </p>
        </div>
      </Card>
    )
  }

  if (activity.type === 'prediction' && activity.match && activity.prediction) {
    const resultType = activity.prediction.resultType
    const resultConfig = {
      exact: { icon: Target, color: 'text-success', bg: 'bg-success/10', label: 'Acertou na mosca!' },
      winner: { icon: ThumbsUp, color: 'text-primary', bg: 'bg-primary/10', label: 'Acertou o vencedor' },
      miss: { icon: X, color: 'text-destructive', bg: 'bg-destructive/10', label: 'Errou' },
    }

    const config = resultType ? resultConfig[resultType] : null

    return (
      <Card className="p-3">
        <div className="flex items-start gap-3">
          <Avatar className="h-10 w-10 shrink-0">
            <AvatarFallback className="text-lg bg-muted">
              {activity.user.avatar}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-medium text-sm">{activity.user.nickname}</span>
              <span className="text-xs text-muted-foreground">{timeAgo}</span>
            </div>
            <div className="mt-2 p-2 rounded-lg bg-muted/50">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span>{activity.match.homeTeam.flag}</span>
                  <span className="font-medium">{activity.match.homeTeam.code}</span>
                </div>
                <div className="flex items-center gap-1 font-bold text-primary">
                  <span>{activity.prediction.homeScore}</span>
                  <span className="text-muted-foreground">-</span>
                  <span>{activity.prediction.awayScore}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{activity.match.awayTeam.code}</span>
                  <span>{activity.match.awayTeam.flag}</span>
                </div>
              </div>
            </div>
            {config && (
              <div className="mt-2 flex items-center gap-2">
                <Badge className={cn('text-xs', config.bg, config.color)}>
                  <config.icon className="h-3 w-3 mr-1" />
                  {config.label}
                </Badge>
                {activity.prediction.points !== undefined && (
                  <Badge variant="outline" className="text-xs">
                    +{activity.prediction.points} pts
                  </Badge>
                )}
              </div>
            )}
          </div>
        </div>
      </Card>
    )
  }

  return null
}
