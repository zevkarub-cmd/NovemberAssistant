import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Card } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import type { FeatureCardItem } from '@/types/navigation'

interface FeatureCardProps {
  item: FeatureCardItem
}

export function FeatureCard({ item }: FeatureCardProps) {
  const Icon = item.icon

  return (
    <Link
      to={item.path}
      className="group block outline-none transition-transform duration-200 active:scale-[0.985] focus-visible:ring-2 focus-visible:ring-ring/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
    >
      <Card
        className={cn(
          'flex-row items-center gap-4 p-4 transition-all duration-200',
          'hover:shadow-[0_14px_40px_rgba(26,20,16,0.12)] dark:hover:shadow-[0_14px_40px_rgba(0,0,0,0.35)]',
          'hover:border-border',
        )}
      >
        <div
          className={cn(
            'flex size-14 shrink-0 items-center justify-center rounded-2xl transition-transform duration-200 group-hover:scale-105',
            item.accentClassName,
          )}
        >
          <Icon className={cn('size-7', item.iconClassName)} strokeWidth={2.1} />
        </div>

        <div className="min-w-0 flex-1">
          <div className="text-[16px] font-semibold tracking-tight text-foreground">
            {item.title}
          </div>
          <p className="mt-0.5 text-sm text-muted-foreground">{item.description}</p>
        </div>

        <ArrowRight
          className="size-4 shrink-0 text-muted-foreground/70 transition-transform duration-200 group-hover:translate-x-0.5 group-hover:text-foreground"
          strokeWidth={2}
        />
      </Card>
    </Link>
  )
}
