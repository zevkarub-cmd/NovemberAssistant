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
    colorScheme: 'light',
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

function readColorScheme(webApp: WebApp): 'light' | 'dark' {
  return webApp.colorScheme === 'dark' ? 'dark' : 'light'
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
    colorScheme: readColorScheme(webApp),
    viewportWidth: typeof window !== 'undefined' ? window.innerWidth : null,
    viewportHeight: webApp.viewportHeight ?? webApp.viewportStableHeight ?? null,
    initDataUnsafe: webApp.initDataUnsafe ?? null,
  }
}

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

async function bootstrapOfficialSdk(): Promise<void> {
  try {
    const sdk = await import('@telegram-apps/sdk')

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
    // Optional SDK path — WebApp remains the source of truth.
  }
}

/**
 * Browser-safe Telegram bootstrap. Never hangs outside Telegram.
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
      // Keep going with whatever data is available.
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

export function subscribeTelegramTheme(
  onChange: (scheme: 'light' | 'dark') => void,
): () => void {
  const webApp = getWebApp()

  if (!webApp) {
    return () => undefined
  }

  const handler = () => {
    onChange(readColorScheme(webApp))
  }

  try {
    webApp.onEvent('themeChanged', handler)
  } catch {
    return () => undefined
  }

  return () => {
    try {
      webApp.offEvent('themeChanged', handler)
    } catch {
      // no-op
    }
  }
}
