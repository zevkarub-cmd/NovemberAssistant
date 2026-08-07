import { useAppStore } from '@/hooks/useAppStore'

export function useTelegramUser() {
  const { user, isTelegram, isBootstrapping } = useAppStore()

  return { user, isTelegram, isBootstrapping }
}
