'use client'

import { createContext, useCallback, useContext, useEffect, useState, ReactNode } from 'react'
import { Group, User } from '@/lib/types'
import { logout as clearSessionToken } from '@/lib/api/auth'
import { getCurrentGroup, listGroups } from '@/lib/api/groups'
import { getCurrentUser } from '@/lib/api/users'
import { ApiError, getAccessToken, isRestApiConfigured } from '@/lib/api/client'

interface AppContextType {
  currentUser: User | null
  setCurrentUser: (user: User | null) => void
  isAuthenticated: boolean
  currentGroup: Group | null
  setCurrentGroup: (group: Group | null) => void
  groups: Group[]
  isLoadingSession: boolean
  refreshGroups: () => Promise<void>
  logout: () => void
  theme: 'light' | 'dark'
  toggleTheme: () => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [currentGroup, setCurrentGroup] = useState<Group | null>(null)
  const [groups, setGroups] = useState<Group[]>([])
  const [isLoadingSession, setIsLoadingSession] = useState(true)
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  const refreshGroups = useCallback(async () => {
    const nextGroups = await listGroups()
    setGroups(nextGroups)
    setCurrentGroup((group) => {
      if (!nextGroups.length) return null
      if (!group) return nextGroups[0]
      return nextGroups.find((item) => item.id === group.id) ?? nextGroups[0]
    })
  }, [])

  const logout = useCallback(() => {
    clearSessionToken()
    setCurrentUser(null)
    setCurrentGroup(null)
    setGroups([])
  }, [])

  useEffect(() => {
    let cancelled = false

    async function loadSession() {
      setIsLoadingSession(true)
      try {
        if (isRestApiConfigured() && !getAccessToken()) {
          if (!cancelled) {
            setCurrentUser(null)
            setCurrentGroup(null)
            setGroups([])
          }
          return
        }

        const [user, userGroups, group] = await Promise.all([
          getCurrentUser(),
          listGroups(),
          getCurrentGroup(),
        ])
        if (cancelled) return
        setCurrentUser(user)
        setGroups(userGroups)
        setCurrentGroup(group)
      } catch (error) {
        if (!cancelled) {
          if (error instanceof ApiError && error.status === 401) {
            logout()
          }
          setCurrentUser(null)
          setCurrentGroup(null)
          setGroups([])
        }
      } finally {
        if (!cancelled) setIsLoadingSession(false)
      }
    }

    loadSession()

    return () => {
      cancelled = true
    }
  }, [logout])

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', newTheme === 'dark')
    }
  }

  return (
    <AppContext.Provider
      value={{
        currentUser,
        setCurrentUser,
        isAuthenticated: !!currentUser,
        currentGroup,
        setCurrentGroup,
        groups,
        isLoadingSession,
        refreshGroups,
        logout,
        theme,
        toggleTheme,
      }}
    >
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}
