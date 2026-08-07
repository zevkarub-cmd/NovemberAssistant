import { useAppStore } from '@/hooks/useAppStore'

export function useTheme() {
  const { colorScheme } = useAppStore()

  return { colorScheme, isDark: colorScheme === 'dark' }
}
