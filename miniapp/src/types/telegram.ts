import type { WebApp } from 'telegram-web-app'

/**
 * Telegram Mini App user profile from WebApp.initDataUnsafe.user
 */
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
}
