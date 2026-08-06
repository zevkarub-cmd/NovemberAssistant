import type { TelegramConnection } from '@/types/telegram'

interface TelegramStatusProps {
  connection: TelegramConnection
}

function Value({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-3 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className="truncate font-medium text-foreground">{value}</span>
    </div>
  )
}

/**
 * Compact Telegram connection status. Does not alter the main UI.
 */
export function TelegramStatus({ connection }: TelegramStatusProps) {
  if (!connection.isReady) {
    return null
  }

  if (!connection.isTelegram) {
    return (
      <div className="rounded-2xl border border-border/60 bg-card px-4 py-3 text-sm text-muted-foreground shadow-[0_8px_30px_rgba(26,20,16,0.06)]">
        Запущено вне Telegram
      </div>
    )
  }

  const { user } = connection

  return (
    <div className="rounded-2xl border border-border/60 bg-card px-4 py-3 shadow-[0_8px_30px_rgba(26,20,16,0.06)]">
      <p className="text-sm font-semibold text-foreground">Подключение успешно</p>
      <div className="mt-2.5 flex flex-col gap-1.5">
        <Value label="ID" value={user?.id != null ? String(user.id) : '—'} />
        <Value label="Username" value={user?.username ? `@${user.username}` : '—'} />
        <Value label="Имя" value={user?.firstName ?? '—'} />
        <Value label="Фамилия" value={user?.lastName ?? '—'} />
        <Value label="Язык" value={user?.languageCode ?? '—'} />
      </div>
    </div>
  )
}
