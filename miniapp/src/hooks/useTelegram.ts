import { useEffect, useState } from 'react'
import { initTelegramApp } from '@/lib/telegram'
import type { TelegramConnection } from '@/types/telegram'

const initialState: TelegramConnection = {
  isReady: false,
  isTelegram: false,
  webApp: null,
  user: null,
}

/**
 * Initializes Telegram.WebApp once and exposes connection + user data.
 * Outside Telegram the app keeps working and reports browser mode.
 */
export function useTelegram(): TelegramConnection {
  const [state, setState] = useState<TelegramConnection>(initialState)

  useEffect(() => {
    setState(initTelegramApp())
  }, [])

  return state
}
