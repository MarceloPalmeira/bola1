'use client'

import { AppProvider } from '@/lib/context'
import { AuthGuard } from '@/components/auth/auth-guard'
import { BottomNav } from '@/components/navigation/bottom-nav'
import { DesktopNav } from '@/components/navigation/desktop-nav'
import { Toaster } from '@/components/ui/sonner'

export default function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <AppProvider>
      <AuthGuard>
        <div className="min-h-screen bg-background">
          <DesktopNav />
          <main className="pb-24 md:pb-8 md:pt-20">
            {children}
          </main>
          <BottomNav />
          <Toaster />
        </div>
      </AuthGuard>
    </AppProvider>
  )
}
