'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useApp } from '@/lib/context'

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoadingSession } = useApp()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (isLoadingSession) return
    if (!isAuthenticated) {
      const search = typeof window !== 'undefined' ? window.location.search : ''
      const next = encodeURIComponent(pathname + search)
      router.replace(`/login?next=${next}`)
    }
  }, [isAuthenticated, isLoadingSession, router, pathname])

  if (isLoadingSession) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <p className="text-sm text-muted-foreground">Carregando...</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}
