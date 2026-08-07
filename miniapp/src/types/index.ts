export type { AppUser, AppThemeState } from './user'
export type { AppRouteId, FeatureCardItem } from './navigation'
export type { TelegramUser, TelegramConnection } from './telegram'

export interface ApiError {
  message: string
  status?: number
}
