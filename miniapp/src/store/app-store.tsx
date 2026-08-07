import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { AppStoreContext, type AppStoreValue } from '@/store/app-context'
import { initTelegramApp, subscribeTelegramTheme } from '@/services/telegram'
import { applyColorScheme } from '@/services/theme'
import { createGuestUser, mapTelegramUser } from '@/services/user'
import type { AppUser } from '@/types/user'

const BOOTSTRAP_TIMEOUT_MS = 1500

interface AppStoreProviderProps {
  children: ReactNode
}

export function AppStoreProvider({ children }: AppStoreProviderProps) {
  const [isBootstrapping, setIsBootstrapping] = useState(true)
  const [isTelegram, setIsTelegram] = useState(false)
  const [user, setUser] = useState<AppUser>(createGuestUser)
  const [colorScheme, setColorScheme] = useState<'light' | 'dark'>('light')

  const finishBootstrap = useCallback((next: {
    isTelegram: boolean
    user: AppUser
    colorScheme: 'light' | 'dark'
  }) => {
    setIsTelegram(next.isTelegram)
    setUser(next.user)
    setColorScheme(next.colorScheme)
    applyColorScheme(next.colorScheme)
    setIsBootstrapping(false)
  }, [])

  useEffect(() => {
    let cancelled = false
    let settled = false

    const finish = (next: {
      isTelegram: boolean
      user: AppUser
      colorScheme: 'light' | 'dark'
    }) => {
      if (cancelled || settled) {
        return
      }

      settled = true
      finishBootstrap(next)
    }

    const timeoutId = window.setTimeout(() => {
      finish({
        isTelegram: false,
        user: createGuestUser(),
        colorScheme: 'light',
      })
    }, BOOTSTRAP_TIMEOUT_MS)

    void initTelegramApp()
      .then((connection) => {
        finish({
          isTelegram: connection.isTelegram,
          user: mapTelegramUser(connection.user),
          colorScheme: connection.colorScheme,
        })
      })
      .catch(() => {
        finish({
          isTelegram: false,
          user: createGuestUser(),
          colorScheme: 'light',
        })
      })
      .finally(() => {
        window.clearTimeout(timeoutId)
      })

    return () => {
      cancelled = true
      window.clearTimeout(timeoutId)
    }
  }, [finishBootstrap])

  useEffect(() => {
    return subscribeTelegramTheme((scheme) => {
      setColorScheme(scheme)
      applyColorScheme(scheme)
    })
  }, [])

  const value = useMemo<AppStoreValue>(
    () => ({
      isBootstrapping,
      isTelegram,
      user,
      colorScheme,
    }),
    [colorScheme, isBootstrapping, isTelegram, user],
  )

  return (
    <AppStoreContext.Provider value={value}>{children}</AppStoreContext.Provider>
  )
}
