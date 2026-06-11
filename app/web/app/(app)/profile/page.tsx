'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { useApp } from '@/lib/context'
import { listPredictionsForUser } from '@/lib/api/predictions'
import { Prediction } from '@/lib/types'
import { 
  User, 
  Trophy, 
  Target, 
  ThumbsUp, 
  X, 
  Moon,
  Sun,
  ChevronRight,
  LogOut,
  Users,
  History,
} from 'lucide-react'

export default function ProfilePage() {
  const { currentUser, theme, toggleTheme, groups: userGroups, logout } = useApp()
  const [userPredictions, setUserPredictions] = useState<Prediction[]>([])

  useEffect(() => {
    let cancelled = false

    async function loadPredictions() {
      const nextPredictions = currentUser ? await listPredictionsForUser(currentUser.id) : []
      if (!cancelled) setUserPredictions(nextPredictions)
    }

    loadPredictions()

    return () => {
      cancelled = true
    }
  }, [currentUser])

  if (!currentUser) {
    return (
      <div className="px-4 py-6 max-w-md mx-auto">
        <Card className="p-8 text-center">
          <div className="text-4xl mb-3">👤</div>
          <p className="font-medium">Não logado</p>
          <Link href="/login">
            <Button className="mt-4">Fazer login</Button>
          </Link>
        </Card>
      </div>
    )
  }

  // Calculate total stats across all groups
  const totalStats = userGroups.reduce((acc, group) => {
    const member = group.members.find(m => m.userId === currentUser.id)
    if (member) {
      acc.totalPoints += member.totalPoints
      acc.exactScores += member.exactScores
      acc.correctWinners += member.correctWinners
      acc.misses += member.misses
    }
    return acc
  }, { totalPoints: 0, exactScores: 0, correctWinners: 0, misses: 0 })

  return (
    <div className="px-4 py-6 max-w-md mx-auto">
      {/* Profile Header */}
      <Card className="p-6 mb-6 text-center">
        <span className="text-6xl block mb-3">{currentUser.avatar}</span>
        <h1 className="text-xl font-bold mb-1">{currentUser.nickname}</h1>
        <p className="text-sm text-muted-foreground">{currentUser.email}</p>
        <div className="mt-4 pt-4 border-t border-border">
          <div className="flex items-center justify-center gap-2">
            <Trophy className="h-5 w-5 text-primary" />
            <span className="text-2xl font-bold text-primary">{totalStats.totalPoints}</span>
            <span className="text-muted-foreground">pontos totais</span>
          </div>
        </div>
      </Card>

      {/* Stats Cards */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <Card className="p-4 text-center">
          <div className="w-10 h-10 rounded-full bg-success/10 flex items-center justify-center mx-auto mb-2">
            <Target className="h-5 w-5 text-success" />
          </div>
          <p className="text-2xl font-bold">{totalStats.exactScores}</p>
          <p className="text-[10px] text-muted-foreground">Placares exatos</p>
        </Card>
        <Card className="p-4 text-center">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-2">
            <ThumbsUp className="h-5 w-5 text-primary" />
          </div>
          <p className="text-2xl font-bold">{totalStats.correctWinners}</p>
          <p className="text-[10px] text-muted-foreground">Vencedores</p>
        </Card>
        <Card className="p-4 text-center">
          <div className="w-10 h-10 rounded-full bg-destructive/10 flex items-center justify-center mx-auto mb-2">
            <X className="h-5 w-5 text-destructive" />
          </div>
          <p className="text-2xl font-bold">{totalStats.misses}</p>
          <p className="text-[10px] text-muted-foreground">Erros</p>
        </Card>
      </div>

      {/* My Groups */}
      <Card className="mb-6">
        <div className="p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">Meus grupos</span>
          </div>
          <Badge variant="secondary">{userGroups.length}</Badge>
        </div>
        <Separator />
        <div className="p-2">
          {userGroups.map((group) => {
            const member = group.members.find(m => m.userId === currentUser.id)
            return (
              <Link key={group.id} href={`/groups/${group.id}`}>
                <div className="flex items-center justify-between p-3 rounded-lg hover:bg-muted transition-colors">
                  <div>
                    <p className="font-medium text-sm">{group.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {member?.totalPoints || 0} pts • {group.members.length} membros
                    </p>
                  </div>
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                </div>
              </Link>
            )
          })}
        </div>
      </Card>

      {/* Prediction History */}
      <Card className="mb-6">
        <div className="p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">Histórico de palpites</span>
          </div>
          <Badge variant="secondary">{userPredictions.length}</Badge>
        </div>
        <Separator />
        <div className="p-4">
          {userPredictions.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              Você ainda não fez nenhum palpite
            </p>
          ) : (
            <div className="space-y-2">
              {userPredictions.slice(0, 5).map((prediction) => (
                <div 
                  key={prediction.id}
                  className="flex items-center justify-between p-2 rounded-lg bg-muted/50"
                >
                  <div className="text-sm">
                    <span>Palpite: </span>
                    <span className="font-bold">{prediction.homeScore} - {prediction.awayScore}</span>
                  </div>
                  {prediction.points != null && (
                    <Badge 
                      variant={prediction.points === 3 ? 'default' : prediction.points === 1 ? 'secondary' : 'outline'}
                      className={prediction.points === 3 ? 'bg-success' : prediction.points === 0 ? 'text-destructive' : ''}
                    >
                      +{prediction.points} pts
                    </Badge>
                  )}
                </div>
              ))}
              {userPredictions.length > 5 && (
                <Button variant="ghost" className="w-full text-sm">
                  Ver todos os {userPredictions.length} palpites
                </Button>
              )}
            </div>
          )}
        </div>
      </Card>

      {/* Settings */}
      <Card>
        <button 
          onClick={toggleTheme}
          className="w-full flex items-center justify-between p-4 hover:bg-muted transition-colors"
        >
          <div className="flex items-center gap-3">
            {theme === 'light' ? (
              <Moon className="h-5 w-5 text-muted-foreground" />
            ) : (
              <Sun className="h-5 w-5 text-muted-foreground" />
            )}
            <span className="font-medium">Tema {theme === 'light' ? 'escuro' : 'claro'}</span>
          </div>
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
        </button>
        <Separator />
        <Link href="/login">
          <button
            className="w-full flex items-center justify-between p-4 hover:bg-muted transition-colors text-destructive"
            onClick={logout}
          >
            <div className="flex items-center gap-3">
              <LogOut className="h-5 w-5" />
              <span className="font-medium">Sair</span>
            </div>
          </button>
        </Link>
      </Card>
    </div>
  )
}
