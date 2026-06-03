'use client'

import Link from 'next/link'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useApp } from '@/lib/context'
import { listUserGroups } from '@/lib/api/groups'
import { Users, Plus, ChevronRight, Crown, UserPlus } from 'lucide-react'

export default function GroupsPage() {
  const { currentUser, currentGroup, setCurrentGroup } = useApp()

  const userGroups = listUserGroups(currentUser?.id)

  return (
    <div className="px-4 py-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Users className="h-5 w-5 text-primary" />
            <h1 className="text-xl font-bold">Meus Grupos</h1>
          </div>
          <p className="text-sm text-muted-foreground">
            {userGroups.length} {userGroups.length === 1 ? 'grupo' : 'grupos'}
          </p>
        </div>
        <Link href="/groups/create">
          <Button size="sm" className="rounded-xl">
            <Plus className="h-4 w-4 mr-2" />
            Criar grupo
          </Button>
        </Link>
      </div>

      {/* Join Group CTA */}
      <Card className="p-4 mb-6 border-dashed border-2 border-primary/30 bg-primary/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <UserPlus className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="font-medium">Recebeu um convite?</p>
              <p className="text-xs text-muted-foreground">Cole o código ou link do grupo</p>
            </div>
          </div>
          <Link href="/groups/join">
            <Button variant="outline" size="sm" className="rounded-xl">
              Entrar
            </Button>
          </Link>
        </div>
      </Card>

      {/* Groups List */}
      <div className="space-y-3">
        {userGroups.map((group) => {
          const member = group.members.find(m => m.userId === currentUser?.id)
          const isAdmin = member?.role === 'admin'
          const isActive = currentGroup?.id === group.id

          return (
            <Card 
              key={group.id}
              className={`p-4 transition-all cursor-pointer hover:shadow-md ${
                isActive ? 'ring-2 ring-primary bg-primary/5' : ''
              }`}
              onClick={() => setCurrentGroup(group)}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold">{group.name}</h3>
                  {isAdmin && (
                    <Badge variant="outline" className="text-[10px]">
                      <Crown className="h-3 w-3 mr-1" />
                      Admin
                    </Badge>
                  )}
                </div>
                {isActive && (
                  <Badge className="bg-primary text-primary-foreground text-[10px]">
                    Ativo
                  </Badge>
                )}
              </div>

              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-4 text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    {group.members.length} membros
                  </span>
                  {member && (
                    <span className="text-primary font-medium">
                      {member.totalPoints} pts
                    </span>
                  )}
                </div>
                <Link href={`/groups/${group.id}`} onClick={(e) => e.stopPropagation()}>
                  <Button variant="ghost" size="sm" className="text-muted-foreground">
                    Ver <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </Link>
              </div>

              {/* Members Preview */}
              <div className="mt-3 pt-3 border-t border-border flex items-center gap-1">
                {group.members.slice(0, 5).map((m) => (
                  <span key={m.userId} className="text-xl" title={m.user.nickname}>
                    {m.user.avatar}
                  </span>
                ))}
                {group.members.length > 5 && (
                  <span className="text-xs text-muted-foreground ml-1">
                    +{group.members.length - 5}
                  </span>
                )}
              </div>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
