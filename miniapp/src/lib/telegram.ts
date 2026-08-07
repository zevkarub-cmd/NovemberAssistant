import type { WebApp, WebAppUser } from 'telegram-web-app'
import type { TelegramConnection, TelegramUser } from '@/types/telegram'

export function emptyConnection(
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
  try {
    if (typeof window === 'undefined') {
      return null
    }

    return window.Telegram?.WebApp ?? null
  } catch {
    return null
  }
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
    user: mapUser(webApp.initDataUnsafe?.user),
    platform: webApp.platform || null,
    version: webApp.version || null,
    colorScheme: webApp.colorScheme ?? null,
    viewportWidth: typeof window !== 'undefined' ? window.innerWidth : null,
    viewportHeight: webApp.viewportHeight ?? webApp.viewportStableHeight ?? null,
    initDataUnsafe: webApp.initDataUnsafe ?? null,
  }
}

/**
 * Sync, hang-free check: real Telegram sessions always provide init data.
 */
function isInsideTelegram(webApp: WebApp | null): webApp is WebApp {
  if (!webApp) {
    return false
  }

  try {
    return Boolean(webApp.initData) || Boolean(webApp.initDataUnsafe?.user)
  } catch {
    return false
  }
}

/**
 * Best-effort @telegram-apps/sdk bootstrap.
 * Never throws and is skipped entirely outside Telegram.
 */
async function bootstrapOfficialSdk(): Promise<void> {
  try {
    const sdk = await import('@telegram-apps/sdk')

    // Sync check only — `isTMA('complete')` can hang in a regular browser.
    if (!sdk.isTMA()) {
      return
    }

    sdk.init()

    if (sdk.mountMiniAppSync.isAvailable()) {
      sdk.mountMiniAppSync()
    }

    if (sdk.miniAppReady.isAvailable()) {
      sdk.miniAppReady()
    }

    if (sdk.mountViewport.isAvailable()) {
      await sdk.mountViewport()
    }

    if (sdk.expandViewport.isAvailable()) {
      sdk.expandViewport()
    }
  } catch {
    // Official SDK is optional — WebApp API is the source of truth for UI data.
  }
}

/**
 * Connects Mini App safely for both Telegram and regular browsers.
 * Guarantees a resolved result without console errors outside Telegram.
 */
export async function initTelegramApp(): Promise<TelegramConnection> {
  try {
    const webApp = getWebApp()

    if (!isInsideTelegram(webApp)) {
      return emptyConnection()
    }

    try {
      webApp.ready()
      webApp.expand()
    } catch {
      // Ignore WebApp method failures — still return available data.
    }

    await bootstrapOfficialSdk()

    return {
      isReady: true,
      isTelegram: true,
      ...readWebAppSnapshot(webApp),
    }
  } catch {
    return emptyConnection()
  }
}

export function getTelegramWebApp(): WebApp | null {
  return getWebApp()
}
