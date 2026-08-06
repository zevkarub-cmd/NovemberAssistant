/**
 * Shared domain types for the Mini App.
 * Extended as API integration grows.
 */

export type MenuItemId =
  | 'opening'
  | 'closing'
  | 'inventory'
  | 'employees'
  | 'stats'
  | 'settings'

export interface MenuItem {
  id: MenuItemId
  title: string
  description: string
  icon: string
  path: string
}

export interface ApiError {
  message: string
  status?: number
}

export type { TelegramUser, TelegramConnection } from './telegram'
