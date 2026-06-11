'use client'

import { useEffect, useState } from 'react'
import { ActivityFeed } from '@/components/activity/activity-feed'
import { useApp } from '@/lib/context'
import { getActivitiesForGroup } from '@/lib/api/activities'
import { Activity as ActivityType } from '@/lib/types'
import { Activity, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'

export default function ActivityPage() {
  const router = useRouter()
  const { currentGroup } = useApp()
  const [activities, setActivities] = useState<ActivityType[]>([])

  useEffect(() => {
    let cancelled = false

    async function loadActivities() {
      const nextActivities = currentGroup ? await getActivitiesForGroup(currentGroup.id) : []
      if (!cancelled) setActivities(nextActivities)
    }

    loadActivities()

    return () => {
      cancelled = true
    }
  }, [currentGroup])

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

      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <Activity className="h-5 w-5 text-primary" />
          <h1 className="text-xl font-bold">Atividade</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          {currentGroup?.name} • {activities.length} atividades
        </p>
      </div>

      {/* Activity Feed */}
      <ActivityFeed activities={activities} />
    </div>
  )
}
