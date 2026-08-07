import { cn } from '@/lib/utils'

interface UserAvatarProps {
  name: string
  className?: string
}

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean)

  if (parts.length === 0) {
    return 'N'
  }

  if (parts.length === 1) {
    return parts[0].slice(0, 2).toUpperCase()
  }

  return `${parts[0][0] ?? ''}${parts[1][0] ?? ''}`.toUpperCase()
}

export function UserAvatar({ name, className }: UserAvatarProps) {
  return (
    <div
      className={cn(
        'relative flex size-14 items-center justify-center overflow-hidden rounded-2xl',
        'bg-gradient-to-br from-accent via-[#c8965a] to-[#8b5e34]',
        'shadow-[0_10px_30px_rgba(138,94,52,0.28)]',
        'ring-2 ring-white/70 dark:ring-white/10',
        className,
      )}
      aria-hidden
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.35),transparent_55%)]" />
      <span className="relative text-lg font-semibold tracking-wide text-white">
        {getInitials(name)}
      </span>
    </div>
  )
}
