import type { WebApp, WebAppInitData } from 'telegram-web-app'

export interface TelegramUser {
  id: number
  username?: string
  firstName?: string
  lastName?: string
  languageCode?: string
}

export interface TelegramConnection {
  isReady: boolean
  isTelegram: boolean
  webApp: WebApp | null
  user: TelegramUser | null
  platform: string | null
  version: string | null
  colorScheme: 'light' | 'dark'
  viewportWidth: number | null
  viewportHeight: number | null
  initDataUnsafe: WebAppInitData | null
}
