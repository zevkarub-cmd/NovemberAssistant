import { useEffect, useState } from 'react'
import { initTelegramApp } from '@/lib/telegram'
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

/**
 * Initializes Telegram Mini Apps SDK once and exposes connection state.
 */
export function useTelegram(): TelegramConnection {
  const [state, setState] = useState<TelegramConnection>(initialState)

  useEffect(() => {
    let cancelled = false

    void initTelegramApp().then((connection) => {
      if (!cancelled) {
        setState(connection)
      }
    })

    return () => {
      cancelled = true
    }
  }, [])

  return state
}
