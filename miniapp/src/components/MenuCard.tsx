import {
  ArrowRight,
  BarChart3,
  Box,
  Moon,
  Settings,
  Sun,
  Users,
  type LucideIcon,
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import type { MenuItem, MenuItemId } from '@/types'

const iconMap: Record<MenuItemId, LucideIcon> = {
  opening: Sun,
  closing: Moon,
  inventory: Box,
  employees: Users,
  stats: BarChart3,
  settings: Settings,
}

const accentMap: Record<MenuItemId, string> = {
  opening: 'bg-amber-50 text-amber-700',
  closing: 'bg-indigo-50 text-indigo-700',
  inventory: 'bg-orange-50 text-orange-700',
  employees: 'bg-emerald-50 text-emerald-700',
  stats: 'bg-sky-50 text-sky-700',
  settings: 'bg-stone-100 text-stone-700',
}

interface MenuCardProps {
  item: MenuItem
  onClick?: () => void
  className?: string
}

export function MenuCard({ item, onClick, className }: MenuCardProps) {
  const Icon = iconMap[item.id]

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'group w-full text-left outline-none transition-transform duration-200',
        'active:scale-[0.985] focus-visible:ring-2 focus-visible:ring-ring/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background',
        className,
      )}
    >
      <Card
        className={cn(
          'flex-row items-center gap-4 p-4 transition-all duration-200',
          'hover:shadow-[0_12px_36px_rgba(26,20,16,0.1)] hover:border-border',
          'group-active:shadow-[0_4px_16px_rgba(26,20,16,0.08)]',
        )}
      >
        <div
          className={cn(
            'flex size-12 shrink-0 items-center justify-center rounded-2xl transition-transform duration-200 group-hover:scale-105',
            accentMap[item.id],
          )}
        >
          <Icon className="size-5" strokeWidth={2.25} />
        </div>

        <div className="min-w-0 flex-1">
          <div className="text-[15px] font-semibold tracking-tight text-foreground">
            {item.title}
          </div>
          <p className="mt-0.5 text-sm leading-snug text-muted-foreground">
            {item.description}
          </p>
        </div>

        <ArrowRight
          className="size-4 shrink-0 text-muted-foreground/70 transition-transform duration-200 group-hover:translate-x-0.5 group-hover:text-foreground"
          strokeWidth={2}
        />
      </Card>
    </button>
  )
}
