import { UserAvatar } from '@/components/UserAvatar'
import { useAppStore } from '@/hooks/useAppStore'

export function AppHeader() {
  const { user } = useAppStore()

  return (
    <header className="animate-in fade-in slide-in-from-top-2 duration-500">
      <div className="text-[1.75rem] font-bold tracking-tight text-foreground">
        ☕ November
      </div>

      <div className="mt-5 flex items-center gap-3.5 rounded-2xl border border-border/60 bg-card/90 p-3.5 shadow-[0_10px_30px_rgba(26,20,16,0.06)] dark:shadow-[0_10px_30px_rgba(0,0,0,0.25)]">
        <UserAvatar name={user.fullName} />

        <div className="min-w-0 flex-1">
          <p className="truncate text-[16px] font-semibold tracking-tight text-foreground">
            {user.fullName}
          </p>
          <p className="mt-0.5 truncate text-sm text-muted-foreground">
            {user.roleLabel}
          </p>
        </div>
      </div>
    </header>
  )
}
