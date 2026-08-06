import type { WebApp, WebAppUser } from 'telegram-web-app'
import type { TelegramConnection, TelegramUser } from '@/types/telegram'

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

/**
 * Detects whether the app is opened inside Telegram.
 * The WebApp object may exist in a regular browser, but without init data.
 */
function isInsideTelegram(webApp: WebApp): boolean {
  return Boolean(webApp.initData) || Boolean(webApp.initDataUnsafe?.user)
}

/**
 * Connects to Telegram Mini Apps via Telegram.WebApp.
 * Calls ready() + expand() when available. Safe outside Telegram.
 */
export function initTelegramApp(): TelegramConnection {
  try {
    const webApp = getWebApp()

    if (!webApp || !isInsideTelegram(webApp)) {
      return {
        isReady: true,
        isTelegram: false,
        webApp,
        user: null,
      }
    }

    webApp.ready()
    webApp.expand()

    return {
      isReady: true,
      isTelegram: true,
      webApp,
      user: mapUser(webApp.initDataUnsafe.user),
    }
  } catch {
    return {
      isReady: true,
      isTelegram: false,
      webApp: null,
      user: null,
    }
  }
}

export function getTelegramWebApp(): WebApp | null {
  return getWebApp()
}
