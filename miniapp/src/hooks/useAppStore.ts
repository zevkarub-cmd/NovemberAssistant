import { useContext } from 'react'
import { AppStoreContext, type AppStoreValue } from '@/store/app-context'

export function useAppStore(): AppStoreValue {
  const context = useContext(AppStoreContext)

  if (!context) {
    throw new Error('useAppStore must be used within AppStoreProvider')
  }

  return context
}
