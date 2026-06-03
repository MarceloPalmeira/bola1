'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, Trophy, Users, User, Calendar, Sun, Moon, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useApp } from '@/lib/context'
import { Button } from '@/components/ui/button'
import { GroupSwitcher } from '@/components/groups/group-switcher'

const navItems = [
  { href: '/dashboard', label: 'Início', icon: Home },
  { href: '/matches', label: 'Jogos', icon: Calendar },
  { href: '/ranking', label: 'Ranking', icon: Trophy },
  { href: '/groups', label: 'Grupos', icon: Users },
  { href: '/profile', label: 'Perfil', icon: User },
]

export function DesktopNav() {
  const pathname = usePathname()
  const { theme, toggleTheme, currentUser } = useApp()

  return (
    <header className="hidden md:flex fixed top-0 left-0 right-0 z-50 border-b border-border bg-card/95 backdrop-blur-lg">
      <div className="w-full max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-2">
            <span className="text-2xl font-bold text-primary">bola1</span>
            <span className="text-xs font-medium text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
              Copa 2026
            </span>
          </Link>
          <nav className="flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'text-primary bg-primary/10'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          <GroupSwitcher />
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="rounded-full"
            aria-label="Alternar tema"
          >
            {theme === 'light' ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </Button>
          <Link href="/admin">
            <Button variant="ghost" size="icon" className="rounded-full" aria-label="Abrir painel admin">
              <Settings className="h-5 w-5" />
            </Button>
          </Link>
          {currentUser && (
            <Link href="/profile" className="flex items-center gap-2 pl-3 border-l border-border">
              <span className="text-2xl">{currentUser.avatar}</span>
              <span className="text-sm font-medium">{currentUser.nickname}</span>
            </Link>
          )}
        </div>
      </div>
    </header>
  )
}
