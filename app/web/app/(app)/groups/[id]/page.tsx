'use client'

import { use, useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { RankingList } from '@/components/ranking/ranking-list'
import { ActivityFeed } from '@/components/activity/activity-feed'
import { useApp } from '@/lib/context'
import { getActivitiesForGroup } from '@/lib/api/activities'
import { getGroup } from '@/lib/api/groups'
import { getRanking } from '@/lib/api/rankings'
import { Activity as ActivityType, Group, RankingEntry } from '@/lib/types'
import { 
  ArrowLeft, 
  Users, 
  Trophy, 
  Activity,
  Share2,
  Crown,
} from 'lucide-react'

interface GroupDetailPageProps {
  params: Promise<{ id: string }>
}

export default function GroupDetailPage({ params }: GroupDetailPageProps) {
  const { id } = use(params)
  const router = useRouter()
  const { currentUser } = useApp()

  const [group, setGroup] = useState<Group | undefined>()
  const [ranking, setRanking] = useState<RankingEntry[]>([])
  const [activities, setActivities] = useState<ActivityType[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function loadGroup() {
      setIsLoading(true)
      try {
        const nextGroup = await getGroup(id)
        const [nextRanking, nextActivities] = nextGroup
          ? await Promise.all([getRanking(id), getActivitiesForGroup(id)])
          : [[], []]
        if (cancelled) return
        setGroup(nextGroup)
        setRanking(nextRanking)
        setActivities(nextActivities)
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    loadGroup()

    return () => {
      cancelled = true
    }
  }, [id])

  if (!group && !isLoading) {
    return (
      <div className="px-4 py-6 max-w-2xl mx-auto">
        <Card className="p-8 text-center">
          <div className="text-4xl mb-3">🤔</div>
          <p className="font-medium">Grupo não encontrado</p>
          <Button variant="outline" className="mt-4" onClick={() => router.back()}>
            Voltar
          </Button>
        </Card>
      </div>
    )
  }

  if (!group) {
    return (
      <div className="px-4 py-6 max-w-2xl mx-auto">
        <Card className="p-8 text-center">
          <p className="font-medium">Carregando grupo...</p>
        </Card>
      </div>
    )
  }

  const currentMember = group.members.find(m => m.userId === currentUser?.id)
  const isAdmin = currentMember?.role === 'admin'

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

      {/* Group Header */}
      <Card className="p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h1 className="text-xl font-bold">{group.name}</h1>
              {isAdmin && (
                <Badge variant="outline" className="text-[10px]">
                  <Crown className="h-3 w-3 mr-1" />
                  Admin
                </Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground">
              {group.members.length} membros
            </p>
          </div>
          <div className="flex gap-2">
            <Link href={`/groups/${id}/invite`}>
              <Button variant="outline" size="sm" className="rounded-xl">
                <Share2 className="h-4 w-4 mr-2" />
                Convidar
              </Button>
            </Link>
          </div>
        </div>

        {/* Members Preview */}
        <div className="flex items-center gap-2 flex-wrap">
          {group.members.slice(0, 8).map((member) => (
            <div 
              key={member.userId}
              className="flex flex-col items-center"
              title={member.user.nickname}
            >
              <span className="text-2xl">{member.user.avatar}</span>
              <span className="text-[10px] text-muted-foreground truncate max-w-[50px]">
                {member.user.nickname}
              </span>
            </div>
          ))}
          {group.members.length > 8 && (
            <div className="flex flex-col items-center">
              <span className="text-lg text-muted-foreground">+{group.members.length - 8}</span>
            </div>
          )}
        </div>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="ranking">
        <TabsList className="w-full grid grid-cols-3 mb-4">
          <TabsTrigger value="ranking" className="text-xs">
            <Trophy className="h-4 w-4 mr-1" />
            Ranking
          </TabsTrigger>
          <TabsTrigger value="members" className="text-xs">
            <Users className="h-4 w-4 mr-1" />
            Membros
          </TabsTrigger>
          <TabsTrigger value="activity" className="text-xs">
            <Activity className="h-4 w-4 mr-1" />
            Atividade
          </TabsTrigger>
        </TabsList>

        <TabsContent value="ranking">
          <RankingList 
            entries={ranking} 
            currentUserId={currentUser?.id}
            showPodium={ranking.length >= 3}
          />
        </TabsContent>

        <TabsContent value="members">
          <Card className="divide-y divide-border overflow-hidden">
            {group.members.map((member) => (
              <div 
                key={member.userId}
                className="flex items-center gap-3 p-4"
              >
                <Avatar className="h-12 w-12">
                  <AvatarFallback className="text-2xl bg-muted">
                    {member.user.avatar}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium truncate">{member.user.nickname}</p>
                    {member.role === 'admin' && (
                      <Badge variant="outline" className="text-[10px]">
                        <Crown className="h-3 w-3 mr-1" />
                        Admin
                      </Badge>
                    )}
                    {member.userId === currentUser?.id && (
                      <Badge variant="secondary" className="text-[10px]">
                        Você
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {member.totalPoints} pontos • {member.exactScores + member.correctWinners + member.misses} palpites
                  </p>
                </div>
              </div>
            ))}
          </Card>
        </TabsContent>

        <TabsContent value="activity">
          <ActivityFeed activities={activities} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
