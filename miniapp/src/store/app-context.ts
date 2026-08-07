import { createContext } from 'react'
import type { AppUser } from '@/types/user'

export interface AppStoreValue {
  isBootstrapping: boolean
  isTelegram: boolean
  user: AppUser
  colorScheme: 'light' | 'dark'
}

export const AppStoreContext = createContext<AppStoreValue | null>(null)
