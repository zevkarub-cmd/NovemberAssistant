import {
  expandViewport,
  init,
  isTMA,
  miniAppReady,
  mountMiniAppSync,
  mountViewport,
} from '@telegram-apps/sdk'
import type { WebApp, WebAppUser } from 'telegram-web-app'
import type { TelegramConnection, TelegramUser } from '@/types/telegram'

function emptyConnection(
  overrides: Partial<TelegramConnection> = {},
): TelegramConnection {
  return {
    isReady: true,
    isTelegram: false,
    webApp: null,
    user: null,
    platform: null,
    version: null,
    colorScheme: null,
    viewportWidth: null,
    viewportHeight: null,
    initDataUnsafe: null,
    ...overrides,
  }
}

function getWebApp(): WebApp | null {
  if (typeof window === 'undefined') {
    return null
  }

  return window.Telegram?.WebApp ?? null
}

function mapUser(user: WebAppUser | undefined): TelegramUser | null {
  if (!user) {
    return null
  }

  return {
    id: user.id,
    username: user.username,
    firstName: user.first_name,
    lastName: user.last_name,
    languageCode: user.language_code,
  }
}

function readWebAppSnapshot(webApp: WebApp): Omit<
  TelegramConnection,
  'isReady' | 'isTelegram'
> {
  return {
    webApp,
    user: mapUser(webApp.initDataUnsafe.user),
    platform: webApp.platform || null,
    version: webApp.version || null,
    colorScheme: webApp.colorScheme,
    viewportWidth: typeof window !== 'undefined' ? window.innerWidth : null,
    viewportHeight: webApp.viewportHeight ?? webApp.viewportStableHeight ?? null,
    initDataUnsafe: webApp.initDataUnsafe ?? null,
  }
}

/**
 * Connects Mini App via @telegram-apps/sdk and Telegram.WebApp.
 * Safe outside Telegram — no throws to the console.
 */
export async function initTelegramApp(): Promise<TelegramConnection> {
  try {
    const insideTelegram = await isTMA('complete')

    if (!insideTelegram) {
      return emptyConnection()
    }

    init()

    if (mountMiniAppSync.isAvailable()) {
      mountMiniAppSync()
    }

    if (miniAppReady.isAvailable()) {
      miniAppReady()
    }

    if (mountViewport.isAvailable()) {
      await mountViewport()
    }

    if (expandViewport.isAvailable()) {
      expandViewport()
    }

    const webApp = getWebApp()

    if (webApp) {
      webApp.ready()
      webApp.expand()

      return {
        isReady: true,
        isTelegram: true,
        ...readWebAppSnapshot(webApp),
      }
    }

    return emptyConnection({ isTelegram: true })
  } catch {
    return emptyConnection()
  }
}

export function getTelegramWebApp(): WebApp | null {
  return getWebApp()
}
