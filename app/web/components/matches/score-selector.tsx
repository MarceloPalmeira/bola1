'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { Minus, Plus, Lock } from 'lucide-react'

interface ScoreSelectorProps {
  homeTeam: { name: string; flag: string | null; code: string }
  awayTeam: { name: string; flag: string | null; code: string }
  initialHomeScore?: number
  initialAwayScore?: number
  onSubmit: (homeScore: number, awayScore: number) => void
  isLocked?: boolean
  isUpdating?: boolean
}

export function ScoreSelector({
  homeTeam,
  awayTeam,
  initialHomeScore,
  initialAwayScore,
  onSubmit,
  isLocked = false,
  isUpdating = false,
}: ScoreSelectorProps) {
  const hasInitialPrediction = initialHomeScore !== undefined && initialAwayScore !== undefined
  const [homeScore, setHomeScore] = useState(initialHomeScore ?? 0)
  const [awayScore, setAwayScore] = useState(initialAwayScore ?? 0)

  const increment = (team: 'home' | 'away') => {
    if (isLocked) return
    if (team === 'home') {
      setHomeScore((prev) => Math.min(prev + 1, 15))
    } else {
      setAwayScore((prev) => Math.min(prev + 1, 15))
    }
  }

  const decrement = (team: 'home' | 'away') => {
    if (isLocked) return
    if (team === 'home') {
      setHomeScore((prev) => Math.max(prev - 1, 0))
    } else {
      setAwayScore((prev) => Math.max(prev - 1, 0))
    }
  }

  const handleSubmit = () => {
    onSubmit(homeScore, awayScore)
  }

  const hasChanged = !hasInitialPrediction || homeScore !== initialHomeScore || awayScore !== initialAwayScore

  return (
    <div className="space-y-6">
      {/* Score Selectors */}
      <div className="flex items-center justify-between gap-4">
        {/* Home Team */}
        <div className="flex-1 flex flex-col items-center gap-3">
          <span className="text-5xl">{homeTeam.flag}</span>
          <div className="text-center">
            <p className="font-bold text-lg">{homeTeam.name}</p>
            <p className="text-xs text-muted-foreground uppercase">{homeTeam.code}</p>
          </div>
          <div className="flex items-center gap-2 mt-2">
            <Button
              variant="outline"
              size="icon"
              className="h-12 w-12 rounded-xl text-lg"
              onClick={() => decrement('home')}
              disabled={isLocked || homeScore === 0}
              aria-label={`Diminuir gols de ${homeTeam.name}`}
            >
              <Minus className="h-5 w-5" />
            </Button>
            <div className={cn(
              'w-20 h-16 flex items-center justify-center rounded-2xl text-4xl font-bold',
              'bg-primary/10 text-primary border-2 border-primary/20'
            )}>
              {homeScore}
            </div>
            <Button
              variant="outline"
              size="icon"
              className="h-12 w-12 rounded-xl text-lg"
              onClick={() => increment('home')}
              disabled={isLocked || homeScore === 15}
              aria-label={`Aumentar gols de ${homeTeam.name}`}
            >
              <Plus className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* VS Divider */}
        <div className="flex flex-col items-center gap-2">
          <span className="text-2xl font-bold text-muted-foreground">X</span>
        </div>

        {/* Away Team */}
        <div className="flex-1 flex flex-col items-center gap-3">
          <span className="text-5xl">{awayTeam.flag}</span>
          <div className="text-center">
            <p className="font-bold text-lg">{awayTeam.name}</p>
            <p className="text-xs text-muted-foreground uppercase">{awayTeam.code}</p>
          </div>
          <div className="flex items-center gap-2 mt-2">
            <Button
              variant="outline"
              size="icon"
              className="h-12 w-12 rounded-xl text-lg"
              onClick={() => decrement('away')}
              disabled={isLocked || awayScore === 0}
              aria-label={`Diminuir gols de ${awayTeam.name}`}
            >
              <Minus className="h-5 w-5" />
            </Button>
            <div className={cn(
              'w-20 h-16 flex items-center justify-center rounded-2xl text-4xl font-bold',
              'bg-primary/10 text-primary border-2 border-primary/20'
            )}>
              {awayScore}
            </div>
            <Button
              variant="outline"
              size="icon"
              className="h-12 w-12 rounded-xl text-lg"
              onClick={() => increment('away')}
              disabled={isLocked || awayScore === 15}
              aria-label={`Aumentar gols de ${awayTeam.name}`}
            >
              <Plus className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Microcopy */}
      {!isLocked && (
        <p className="text-center text-sm text-muted-foreground">
          {homeScore === awayScore && homeScore > 0
            ? 'Empate? Tá confiante nessa?'
            : homeScore > awayScore + 2 || awayScore > homeScore + 2
            ? 'Esse placar é coragem ou loucura?'
            : 'Manda o palpite!'}
        </p>
      )}

      {/* Submit Button */}
      <Button
        className={cn(
          'w-full h-14 text-lg font-semibold rounded-2xl',
          isLocked
            ? 'bg-muted text-muted-foreground cursor-not-allowed'
            : 'bg-primary text-primary-foreground hover:bg-primary/90'
        )}
        onClick={handleSubmit}
        disabled={isLocked || isUpdating || (hasInitialPrediction && !hasChanged)}
      >
        {isLocked ? (
          <>
            <Lock className="h-5 w-5 mr-2" />
            Palpite travado
          </>
        ) : isUpdating ? (
          'Atualizando...'
        ) : hasInitialPrediction && !hasChanged ? (
          'Palpite registrado'
        ) : hasInitialPrediction ? (
          'Atualizar palpite'
        ) : (
          'Confirmar palpite'
        )}
      </Button>
    </div>
  )
}
