import { useEffect, useState } from 'react'
import { emptyConnection, initTelegramApp } from '@/lib/telegram'
import type { TelegramConnection } from '@/types/telegram'

const initialState: TelegramConnection = {
  isReady: false,
  isTelegram: false,
  webApp: null,
  user: null,
  platform: null,
  version: null,
  colorScheme: null,
  viewportWidth: null,
  viewportHeight: null,
  initDataUnsafe: null,
}

const INIT_TIMEOUT_MS = 1500

/**
 * Initializes Telegram connection once.
 * Always resolves to a ready state (browser-safe timeout fallback).
 */
export function useTelegram(): TelegramConnection {
  const [state, setState] = useState<TelegramConnection>(initialState)

  useEffect(() => {
    let cancelled = false

    const timeoutId = window.setTimeout(() => {
      if (!cancelled) {
        setState((current) =>
          current.isReady ? current : emptyConnection(),
        )
      }
    }, INIT_TIMEOUT_MS)

    void initTelegramApp()
      .then((connection) => {
        if (!cancelled) {
          setState(connection)
        }
      })
      .catch(() => {
        if (!cancelled) {
          setState(emptyConnection())
        }
      })
      .finally(() => {
        window.clearTimeout(timeoutId)
      })

    return () => {
      cancelled = true
      window.clearTimeout(timeoutId)
    }
  }, [])

  return state
}
