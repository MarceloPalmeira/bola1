'use client'

import { createContext, useContext, useState, ReactNode } from 'react'
import { Group, User } from '@/lib/types'
import { getCurrentGroup, listGroups } from '@/lib/api/groups'
import { getCurrentUser } from '@/lib/api/users'

interface AppContextType {
  currentUser: User | null
  setCurrentUser: (user: User | null) => void
  isAuthenticated: boolean
  currentGroup: Group | null
  setCurrentGroup: (group: Group | null) => void
  groups: Group[]
  theme: 'light' | 'dark'
  toggleTheme: () => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
  // Fixture-backed session until backend auth is connected.
  const [currentUser, setCurrentUser] = useState<User | null>(getCurrentUser())
  const [currentGroup, setCurrentGroup] = useState<Group | null>(getCurrentGroup())
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  const groups = listGroups()

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
