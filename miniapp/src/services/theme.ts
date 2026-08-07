/**
 * Applies Telegram color scheme to the document root.
 */
export function applyColorScheme(scheme: 'light' | 'dark'): void {
  const root = document.documentElement

  root.classList.toggle('dark', scheme === 'dark')
  root.style.colorScheme = scheme
}
