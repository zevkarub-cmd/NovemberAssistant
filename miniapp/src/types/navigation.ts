import type { LucideIcon } from 'lucide-react'

export type AppRouteId =
  | 'opening'
  | 'closing'
  | 'inventory'
  | 'employees'
  | 'tasks'
  | 'stats'
  | 'settings'

export interface FeatureCardItem {
  id: AppRouteId
  title: string
  description: string
  path: string
  icon: LucideIcon
  accentClassName: string
  iconClassName: string
}
