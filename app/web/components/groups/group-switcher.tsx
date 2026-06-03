'use client'

import { useApp } from '@/lib/context'
import { ChevronDown, Check } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'

export function GroupSwitcher() {
  const { currentGroup, setCurrentGroup, groups } = useApp()

  if (!currentGroup) return null

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        className="inline-flex items-center justify-center gap-2 px-3 h-9 bg-card border border-border rounded-xl text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        <span className="max-w-[120px] truncate">
          {currentGroup.name}
        </span>
        <ChevronDown className="h-4 w-4 text-muted-foreground" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        {groups.map((group) => (
          <DropdownMenuItem
            key={group.id}
            onClick={() => setCurrentGroup(group)}
            className={cn(
              'flex items-center justify-between gap-2 cursor-pointer',
              currentGroup.id === group.id && 'bg-primary/10'
            )}
          >
            <div className="flex flex-col">
              <span className="font-medium">{group.name}</span>
              <span className="text-xs text-muted-foreground">
                {group.members.length} membros
              </span>
            </div>
            {currentGroup.id === group.id && (
              <Check className="h-4 w-4 text-primary" />
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
