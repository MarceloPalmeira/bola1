'use client'

import { Card } from '@/components/ui/card'
import { RankingList } from '@/components/ranking/ranking-list'
import { useApp } from '@/lib/context'
import { getRanking } from '@/lib/api/rankings'
import { Trophy, Info } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

export default function RankingPage() {
  const { currentUser, currentGroup } = useApp()
  const ranking = currentGroup ? getRanking(currentGroup.id) : []

  return (
    <div className="px-4 py-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <Trophy className="h-5 w-5 text-primary" />
          <h1 className="text-xl font-bold">Ranking</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          {currentGroup?.name} • {ranking.length} participantes
        </p>
      </div>

      {/* Scoring Legend */}
      <Card className="p-4 mb-6 bg-muted/50">
        <div className="flex items-start gap-2">
          <Info className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
          <div className="text-xs text-muted-foreground space-y-1">
            <p><strong>Legenda:</strong></p>
            <div className="flex flex-wrap gap-3">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-success" />
                Placares exatos
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-primary" />
                Vencedores/empates
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-destructive" />
                Erros
              </span>
            </div>
          </div>
        </div>
      </Card>

      {/* Ranking */}
      {ranking.length === 0 ? (
        <Card className="p-8 text-center">
          <div className="text-4xl mb-3">🏆</div>
          <p className="font-medium">Ranking ainda vazio</p>
          <p className="text-sm text-muted-foreground">
            Os palpites serão calculados assim que os jogos terminarem!
          </p>
        </Card>
      ) : (
        <RankingList 
          entries={ranking} 
          currentUserId={currentUser?.id}
          showPodium={ranking.length >= 3}
        />
      )}
    </div>
  )
}
