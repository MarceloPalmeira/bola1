'use client'

import { Card } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { RankingEntry } from '@/lib/types'
import { cn } from '@/lib/utils'
import { Trophy, Target, ThumbsUp, X } from 'lucide-react'

interface RankingListProps {
  entries: RankingEntry[]
  currentUserId?: string
  showPodium?: boolean
}

export function RankingList({ entries, currentUserId, showPodium = true }: RankingListProps) {
  const topThree = entries.slice(0, 3)
  const rest = entries.slice(3)

  return (
    <div className="space-y-4">
      {/* Podium */}
      {showPodium && topThree.length >= 3 && (
        <div className="flex items-end justify-center gap-2 py-4 px-2">
          {/* 2nd Place */}
          <PodiumCard entry={topThree[1]} position={2} isCurrentUser={topThree[1].user.id === currentUserId} />
          
          {/* 1st Place */}
          <PodiumCard entry={topThree[0]} position={1} isCurrentUser={topThree[0].user.id === currentUserId} />
          
          {/* 3rd Place */}
          <PodiumCard entry={topThree[2]} position={3} isCurrentUser={topThree[2].user.id === currentUserId} />
        </div>
      )}

      {/* Full List */}
      <Card className="divide-y divide-border overflow-hidden">
        {entries.map((entry) => (
          <RankingRow
            key={entry.user.id}
            entry={entry}
            isCurrentUser={entry.user.id === currentUserId}
          />
        ))}
      </Card>
    </div>
  )
}

function PodiumCard({
  entry,
  position,
  isCurrentUser,
}: {
  entry: RankingEntry
  position: 1 | 2 | 3
  isCurrentUser: boolean
}) {
  const heights = { 1: 'h-32', 2: 'h-24', 3: 'h-20' }
  const medals = {
    1: { emoji: '🥇', bg: 'bg-gradient-to-b from-yellow-400 to-yellow-500' },
    2: { emoji: '🥈', bg: 'bg-gradient-to-b from-gray-300 to-gray-400' },
    3: { emoji: '🥉', bg: 'bg-gradient-to-b from-amber-600 to-amber-700' },
  }

  return (
    <div className={cn('flex flex-col items-center', position === 1 && '-mt-4')}>
      <span className="text-3xl mb-2">{entry.user.avatar}</span>
      <p className={cn(
        'font-semibold text-sm text-center truncate max-w-[80px]',
        isCurrentUser && 'text-primary'
      )}>
        {entry.user.nickname}
      </p>
      <p className="text-lg font-bold text-primary">{entry.totalPoints} pts</p>
      <div className={cn(
        'w-20 flex flex-col items-center justify-end rounded-t-xl mt-2',
        heights[position],
        medals[position].bg
      )}>
        <span className="text-2xl mb-2">{medals[position].emoji}</span>
      </div>
    </div>
  )
}

function RankingRow({
  entry,
  isCurrentUser,
}: {
  entry: RankingEntry
  isCurrentUser: boolean
}) {
  return (
    <div className={cn(
      'flex items-center gap-3 p-4 transition-colors',
      isCurrentUser && 'bg-primary/5'
    )}>
      {/* Position */}
      <div className={cn(
        'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold',
        entry.position === 1 && 'bg-yellow-100 text-yellow-700',
        entry.position === 2 && 'bg-gray-100 text-gray-700',
        entry.position === 3 && 'bg-amber-100 text-amber-700',
        entry.position > 3 && 'bg-muted text-muted-foreground'
      )}>
        {entry.position}
      </div>

      {/* Avatar */}
      <Avatar className="h-10 w-10">
        <AvatarFallback className="text-xl bg-muted">
          {entry.user.avatar}
        </AvatarFallback>
      </Avatar>

      {/* Name */}
      <div className="flex-1 min-w-0">
        <p className={cn(
          'font-medium truncate',
          isCurrentUser && 'text-primary'
        )}>
          {entry.user.nickname}
          {isCurrentUser && (
            <Badge variant="outline" className="ml-2 text-[10px]">
              Você
            </Badge>
          )}
        </p>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Target className="h-3 w-3 text-success" />
            {entry.exactScores}
          </span>
          <span className="flex items-center gap-1">
            <ThumbsUp className="h-3 w-3 text-primary" />
            {entry.correctWinners}
          </span>
          <span className="flex items-center gap-1">
            <X className="h-3 w-3 text-destructive" />
            {entry.misses}
          </span>
        </div>
      </div>

      {/* Points */}
      <div className="text-right">
        <p className="text-lg font-bold text-primary">{entry.totalPoints}</p>
        <p className="text-[10px] text-muted-foreground uppercase">pontos</p>
      </div>
    </div>
  )
}
