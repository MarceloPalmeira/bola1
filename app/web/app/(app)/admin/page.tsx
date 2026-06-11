'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { listGroups } from '@/lib/api/groups'
import { listMatches, phaseLabels, registerMatchResult } from '@/lib/api/matches'
import { listUsers } from '@/lib/api/users'
import { ApiError } from '@/lib/api/client'
import { Group, Match, User } from '@/lib/types'
import { 
  ArrowLeft,
  Shield,
  Calendar,
  Users,
  Trophy,
  RefreshCw,
  AlertTriangle,
  Plus,
  Pencil,
  Trash2,
  Check,
  Database,
  Ban,
} from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

export default function AdminPage() {
  const router = useRouter()
  const [selectedMatch, setSelectedMatch] = useState<string | null>(null)
  const [homeScore, setHomeScore] = useState('')
  const [awayScore, setAwayScore] = useState('')
  const [matches, setMatches] = useState<Match[]>([])
  const [groups, setGroups] = useState<Group[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [isRegisteringResult, setIsRegisteringResult] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function loadAdminData() {
      const [nextMatches, nextGroups, nextUsers] = await Promise.all([
        listMatches(),
        listGroups(),
        listUsers(),
      ])
      if (cancelled) return
      setMatches(nextMatches)
      setGroups(nextGroups)
      setUsers(nextUsers)
    }

    loadAdminData()

    return () => {
      cancelled = true
    }
  }, [])

  const handleSyncMatches = () => {
    toast.success('Sincronização iniciada', {
      description: 'Os jogos serão atualizados em breve',
    })
  }

  const handleRecalculatePoints = () => {
    toast.success('Recálculo iniciado', {
      description: 'Os pontos serão recalculados em breve',
    })
  }

  const handleRegisterResult = async () => {
    if (!selectedMatch || homeScore === '' || awayScore === '') {
      toast.error('Preencha todos os campos')
      return
    }
    setIsRegisteringResult(true)
    try {
      const updatedMatch = await registerMatchResult(selectedMatch, Number(homeScore), Number(awayScore))
      if (updatedMatch) {
        setMatches((items) => items.map((match) => match.id === updatedMatch.id ? updatedMatch : match))
      }
      toast.success('Resultado registrado!', {
        description: `Placar: ${homeScore} x ${awayScore}`,
      })
      setSelectedMatch(null)
      setHomeScore('')
      setAwayScore('')
    } catch (error) {
      toast.error('Não foi possível registrar o resultado', {
        description: error instanceof ApiError ? error.message : 'Confira suas permissões e tente novamente',
      })
    } finally {
      setIsRegisteringResult(false)
    }
  }

  return (
    <div className="px-4 py-6 max-w-4xl mx-auto">
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

      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-destructive/10 flex items-center justify-center">
          <Shield className="h-6 w-6 text-destructive" />
        </div>
        <div>
          <h1 className="text-xl font-bold">Painel Admin</h1>
          <p className="text-sm text-muted-foreground">Gerenciamento do bolão</p>
        </div>
      </div>

      {/* Warning Card */}
      <Card className="p-4 mb-6 border-destructive/30 bg-destructive/5">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-destructive shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-destructive">Área restrita</p>
            <p className="text-sm text-muted-foreground">
              As ações nesta página afetam todos os usuários. Use com cuidado.
            </p>
          </div>
        </div>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="matches">
        <TabsList className="w-full grid grid-cols-3 mb-6">
          <TabsTrigger value="matches" className="text-xs">
            <Calendar className="h-4 w-4 mr-1" />
            Jogos
          </TabsTrigger>
          <TabsTrigger value="groups" className="text-xs">
            <Users className="h-4 w-4 mr-1" />
            Grupos
          </TabsTrigger>
          <TabsTrigger value="points" className="text-xs">
            <Trophy className="h-4 w-4 mr-1" />
            Pontuação
          </TabsTrigger>
        </TabsList>

        {/* Matches Tab */}
        <TabsContent value="matches" className="space-y-6">
          {/* Sync Matches */}
          <Card className="p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Database className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="font-medium">Sincronizar jogos</p>
                  <p className="text-xs text-muted-foreground">
                    Buscar jogos de API externa (placeholder)
                  </p>
                </div>
              </div>
              <Button variant="outline" onClick={handleSyncMatches}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Sincronizar
              </Button>
            </div>
          </Card>

          {/* Register Result */}
          <Card className="p-4">
            <h3 className="font-medium mb-4 flex items-center gap-2">
              <Check className="h-4 w-4" />
              Registrar resultado
            </h3>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Selecione o jogo</Label>
                <Select value={selectedMatch || ''} onValueChange={setSelectedMatch}>
                  <SelectTrigger>
                    <SelectValue placeholder="Escolha um jogo" />
                  </SelectTrigger>
                  <SelectContent>
                    {matches
                      .filter(m => m.status === 'upcoming' || m.status === 'live' || m.status === 'locked')
                      .map((match) => (
                        <SelectItem key={match.id} value={match.id}>
                          {match.homeTeam.flag} {match.homeTeam.name} vs {match.awayTeam.name} {match.awayTeam.flag}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Gols mandante</Label>
                  <Input 
                    type="number" 
                    min="0" 
                    value={homeScore}
                    onChange={(e) => setHomeScore(e.target.value)}
                    placeholder="0"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Gols visitante</Label>
                  <Input 
                    type="number" 
                    min="0"
                    value={awayScore}
                    onChange={(e) => setAwayScore(e.target.value)}
                    placeholder="0"
                  />
                </div>
              </div>
              <Button 
                className="w-full" 
                onClick={handleRegisterResult}
                disabled={!selectedMatch || homeScore === '' || awayScore === '' || isRegisteringResult}
              >
                {isRegisteringResult ? 'Registrando...' : 'Registrar resultado'}
              </Button>
            </div>
          </Card>

          {/* Matches List */}
          <Card>
            <div className="p-4 border-b border-border">
              <h3 className="font-medium">Todos os jogos</h3>
              <p className="text-xs text-muted-foreground">{matches.length} jogos cadastrados</p>
            </div>
            <div className="divide-y divide-border max-h-96 overflow-y-auto">
              {matches.map((match) => (
                <div key={match.id} className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="text-sm">
                      <p className="font-medium">
                        {match.homeTeam.flag} {match.homeTeam.name} vs {match.awayTeam.name} {match.awayTeam.flag}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {match.date} • {match.time} • {phaseLabels[match.phase]}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant="secondary"
                      className={cn(
                        'text-[10px]',
                        match.status === 'finished' && 'bg-success/20 text-success',
                        match.status === 'live' && 'bg-destructive/20 text-destructive',
                      )}
                    >
                      {match.status === 'finished' && `${match.homeScore} - ${match.awayScore}`}
                      {match.status !== 'finished' && match.status}
                    </Badge>
                    <Button variant="ghost" size="icon" aria-label="Editar jogo">
                      <Pencil className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Add Match */}
          <Card className="p-4 border-dashed border-2">
            <Button variant="outline" className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              Adicionar jogo manualmente
            </Button>
          </Card>
        </TabsContent>

        {/* Groups Tab */}
        <TabsContent value="groups" className="space-y-6">
          <Card>
            <div className="p-4 border-b border-border">
              <h3 className="font-medium">Grupos cadastrados</h3>
              <p className="text-xs text-muted-foreground">{groups.length} grupos</p>
            </div>
            <div className="divide-y divide-border">
              {groups.map((group) => (
                <div key={group.id} className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="font-medium">{group.name}</p>
                      <p className="text-xs text-muted-foreground">
                        Código: {group.code} • {group.members.length} membros
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="icon" aria-label="Editar grupo">
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="text-destructive" aria-label="Excluir grupo">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {group.members.map((member) => (
                      <div 
                        key={member.userId}
                        className="flex items-center gap-2 px-2 py-1 rounded-full bg-muted text-xs"
                      >
                        <span>{member.user.avatar}</span>
                        <span>{member.user.nickname}</span>
                        {member.role === 'admin' && (
                          <Badge variant="outline" className="text-[8px] px-1">Admin</Badge>
                        )}
                        <button className="text-destructive hover:bg-destructive/10 rounded-full p-0.5" aria-label={`Remover ${member.user.nickname} do grupo`}>
                          <Ban className="h-3 w-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-4 border-dashed border-2">
            <Button variant="outline" className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              Criar grupo
            </Button>
          </Card>
        </TabsContent>

        {/* Points Tab */}
        <TabsContent value="points" className="space-y-6">
          {/* Recalculate Points */}
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <RefreshCw className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="font-medium">Recalcular pontuação</p>
                  <p className="text-xs text-muted-foreground">
                    Recalcula todos os pontos baseado nos resultados
                  </p>
                </div>
              </div>
              <Button variant="outline" onClick={handleRecalculatePoints}>
                Recalcular
              </Button>
            </div>
          </Card>

          {/* Scoring Rules */}
          <Card className="p-4">
            <h3 className="font-medium mb-4">Regras de pontuação</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-success/10">
                <span className="text-sm">Placar exato</span>
                <Badge className="bg-success text-success-foreground">3 pontos</Badge>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-primary/10">
                <span className="text-sm">Vencedor ou empate correto</span>
                <Badge className="bg-primary text-primary-foreground">1 ponto</Badge>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted">
                <span className="text-sm">Errou resultado</span>
                <Badge variant="outline">0 pontos</Badge>
              </div>
            </div>
          </Card>

          {/* Manual Score Edit */}
          <Card className="p-4 border-destructive/30">
            <div className="flex items-start gap-3 mb-4">
              <AlertTriangle className="h-5 w-5 text-destructive shrink-0" />
              <div>
                <p className="font-medium text-destructive">Edição manual de pontos</p>
                <p className="text-xs text-muted-foreground">
                  Use apenas em casos excepcionais
                </p>
              </div>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Usuário</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione" />
                    </SelectTrigger>
                    <SelectContent>
                      {users.map((user) => (
                        <SelectItem key={user.id} value={user.id}>
                          {user.avatar} {user.nickname}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Ajuste de pontos</Label>
                  <Input type="number" placeholder="+3 ou -1" />
                </div>
              </div>
              <Button variant="destructive" className="w-full">
                Aplicar ajuste
              </Button>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
